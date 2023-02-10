<script setup lang="ts">
  import { ref, reactive } from 'vue'
  import Home from './components/Home.vue'
  import Play from './components/Play.vue'
  import View from './components/View.vue'

  ////////////
  // 型情報  //
  ////////////
  //
  // home.Vueから受け取る動画再生に必要な情報
  // 月毎動画の場合（指定のyyyymmdd内のすべての動画）
  // [
  //   {"fileName": ["xxx.mp4"], "totalTime: [33.0]"},  # 1つ目のサムネイルに対応
  //   {"fileName": ["yyy.mp4"], "totalTime: [14.2]"},  # 2つ目のサムネイルに対応
  //   {"fileName": ["zzz.mp4"], "totalTime: [33.3]"}   # 3つ目のサムネイルに対応
  // ]
  // ALL動画の場合（ALL内のすべての動画）
  // [
  //   {"fileName": ["xxx-1.mp4", "xxx-2.mp4"], "totalTime: [33.0, 65.1]"},  # 1つ目のサムネイルに対応
  //   {"fileName": ["yyy-1.mp4", "yyy-2.mp4", "yyy-3.mp4"], "totalTime: [14.2, 14.2, 76.5]"},   # 2つ目のサムネイルに対応
  //   {"fileName": ["zzz.mp4"], "totalTime: [33.3]"}  # 3つ目のサムネイルに対応
  // ]
  type InfoPlayMovieOrg = {
    fileName: string[];
    totalTime: number[];
    id: number;
  }[]
  // Play.vueに渡す動画再生に必要な情報
  // short動画の場合、InfoPlayMovieOrgの情報をそのまま型変換
  // long動画の場合、InfoPlayMovieOrgから選択したサムネイルの情報のみを抽出
  type InfoPlayMovie = {
    fileName: string;
    totalTime: number;
  }[]

  // 写真再生に必要な情報（指定のyyyymmdd内のすべての写真情報）
  type InfoPlayPhoto = {
    fileName: string;
    date: string;
    id: number;
  }[]

  // 初期値
  let currentPage = ref("home")  // 現在のページ（home or play）
  let isLong = ref(true)  // playに遷移する際、longが指定されたか否か（longならばtrue, shortならばfalse）
  let indexPlay = ref(0)  // infoPlayXXXXの何番目が再生されるか
  let infoPlayMovie:InfoPlayMovie = reactive([])
  let infoPlayPhoto:InfoPlayPhoto = reactive([])
  let selectedYYYYMM = ref(0)  // 何年何月が選択されたか、0はALL

  // 動画のサムネイルクリック時に発火するイベント（Thumb.vue -> Home.vue -> App.vueと伝搬）
  const goToPlayMovie = (infoOrg:InfoPlayMovieOrg, index:number, isLongFlag: boolean) => {
    currentPage.value = "play"
    isLong.value = isLongFlag
    infoPlayMovie = []
    if (isLong.value){
      for(let i = 0; i < infoOrg[index].fileName.length; i++){
        infoPlayMovie.push({"fileName": infoOrg[index].fileName[i], "totalTime": infoOrg[index].totalTime[i]})
      }
      indexPlay.value = 0
    } else {
      for(let i = 0; i < infoOrg.length; i++){
        infoPlayMovie.push({"fileName": infoOrg[i].fileName[0], "totalTime": infoOrg[i].totalTime[0]})
      }
      indexPlay.value = index
    }
  }
  // 画像のサムネイルクリック時に発火するイベント（Thumb.vue -> Home.vue -> App.vueと伝搬）
  const goToPlayPhoto = (info:InfoPlayPhoto, index:number) => { // id：何番目のサムネイルがクリックされたか
    infoPlayPhoto = info
    indexPlay.value = index
    currentPage.value = "view"
  }

  // 再生画面でhomeボタンを押したときに発火するイベント
  const goToHome = () => {
    currentPage.value = "home"
  }

  // home画面で、月の選択ボタンをした時に発火するイベント
  const changeYYYYMM = (yyyymm:number) => {
    selectedYYYYMM.value = yyyymm
    window.scroll({top: 0});
  }
</script>

<template>
  <body>
    <Suspense v-if="currentPage === 'home'">
      <Home @go-to-play-movie="goToPlayMovie"
            @go-to-play-photo="goToPlayPhoto"
            @change-yyyymm="changeYYYYMM"
            :selectedYYYYMM="selectedYYYYMM"/>
    </Suspense>
    <Play v-if="currentPage === 'play'"
          :infoPlayMovie="infoPlayMovie"
          :index=indexPlay
          @go-to-home="goToHome" />
    <View v-if="currentPage === 'view'"
          :infoPlay="infoPlayPhoto"
          :index=indexPlay
          @go-to-home="goToHome" />
  </body>
</template>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP&family=Roboto&display=swap');
  #app {
    font-family: 'Roboto', 'Noto Sans JP', sans-serif;
  }
</style>