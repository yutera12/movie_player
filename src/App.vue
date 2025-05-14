<script setup lang="ts">
  import { ref, reactive } from 'vue'
  import Home from './components/Home.vue'
  import Play from './components/Play.vue'
  import View from './components/View.vue'


  type InfoPlayMovie = {
    fileName: string;
    totalTime: number;
    id: number
  }[]
  type InfoPlayPhoto = {
    fileName: string;
    date: string;
    id: number;
  }[]

  // 初期値
  let currentPage = ref("home") // 現在のページ（home or play）
  let indexPlay = ref(0)  // infoPlayXXXXの何番目が再生されるか
  let infoPlayMovie:InfoPlayMovie = reactive([])
  let infoPlayPhoto:InfoPlayPhoto = reactive([])
  let selectedYYYYMM = ref(0)  // 何年何月が選択されたか、0はPlayList
  let currentTag = ref("")  // Playlistの選択結果

  // 動画のサムネイルクリック時に発火するイベント（Thumb.vue -> Home.vue -> App.vueと伝搬）
  const goToPlayMovie = (x:InfoPlayMovie, index:number) => {
    currentPage.value = "play"
    indexPlay.value = index
    infoPlayMovie = x
  }
  // 画像のサムネイルクリック時に発火するイベント（Thumb.vue -> Home.vue -> App.vueと伝搬）
  const goToPlayPhoto = (x:InfoPlayPhoto, index:number) => { // id：何番目のサムネイルがクリックされたか
    currentPage.value = "view"
    indexPlay.value = index
    infoPlayPhoto = x
  }

  // 再生画面でhomeボタンを押したときに発火するイベント
  const goToHome = () => {
    currentPage.value = "home"
  }

  // playlist選択画面でplaylistが選択された場合に発火するイベント
  const selectTag = (tag: string) => {
    currentTag.value = tag
  }

  // 個別のplaylist画面でplaylistに戻るリンクがクリックされた場合に発火するイベント
  const goToPlaylist = () => {
    currentTag.value = ''
  }

  // home画面で、月の選択ボタンをした時に発火するイベント
  const changeYYYYMM = (yyyymm:number) => {
    if (yyyymm == 0){
      currentTag.value = ''
    }
    selectedYYYYMM.value = yyyymm
    window.scroll({top: 0});
  }
</script>

<template>
  <body>
    <Suspense v-if="currentPage === 'home'">
      <Home @go-to-play-movie="goToPlayMovie"
            @go-to-play-photo="goToPlayPhoto"
            @go-to-playlist="goToPlaylist"
            @select-tag="selectTag"
            @change-yyyymm="changeYYYYMM"
            :selectedYYYYMM="selectedYYYYMM"
            :currentTag="currentTag"/>
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