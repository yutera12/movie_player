<script setup lang="ts">
  import { onMounted } from 'vue'
  import Nav from './Nav.vue'
  import Thumb from './Thumb.vue'
  import PlayList from './PlayList.vue'
  import axios from 'axios'

  //////////////////////////
  // info_vue.jsonの読み込み //
  //////////////////////////
  type InfoVue = {
    yearMonthList: number[],
    yearList: number[],
    monthList: number[][]
    birthText: {[key in number]: string}
    gant: {"name": string; "gant": {[key in string]: number[]}}[]
    yyyymm2pos: {[key in number]: number}
    yyyymm2text: {[key in number]: string}
    thumbPhoto: {[key in number]: {fileName: string; id: number; date: string; aspectRatio: number;}[]}
    playPhoto: {[key in number]:{fileName: string; date: string; id: number;}[]}
    thumbMovie: {[key in number]: {fileName: string; id: number; totalTime: string; date: string; aspectRatio: number; title:string;}[]}
    playMovie: {[key in number]: {totalTime: number[]; fileName: string[]; id: number;}[]}
    playList: {
      "thumbnail": {[key in string]: {[tag in string]: {"fileName": string, "id": number, "date": string, "aspectRatio": number}[]}},
      "play": {"movie": {[tag in string]: {"fileName": string, "totalTime": number, "id": number}[]},
               "photo": {[tag in string]: {"fileName": string, "date": string, "id": number}[]}}
    }
  }
  let infoVue:InfoVue = {
    "yearMonthList": [],
    "yearList": [],
    "monthList": [[]],
    "birthText": {0: ""},
    "gant":[],
    "yyyymm2pos":{},
    "yyyymm2text":{},
    "thumbPhoto": {},
    "playPhoto": {},
    "thumbMovie": {},
    "playMovie": {},
    "playList": {"thumbnail": {}, "play": {"movie": {}, "photo": {}}}}
  await axios.get("images/info_vue.json").then(function(response) {
    infoVue = response.data
  })

  // App.vueから情報を受けとり
  const props = defineProps<{
    selectedYYYYMM: number
    currentTag: string
  }>();

  // App.vueで定義されるイベントを発火
  const emit = defineEmits(['go-to-play-movie', 'go-to-play-photo', 'select-tag', 'change-yyyymm', 'go-to-playlist'])
  const goToPlay = (index: number, isMovie:boolean) => { // 何番目のサムネイルをクリックしたかを受け取る
    if (isMovie){
      if (props.selectedYYYYMM == 0){
        emit('go-to-play-movie', infoVue["playList"]["play"]["movie"][props.currentTag], index)
      } else {
        emit('go-to-play-movie', infoVue["playMovie"][props.selectedYYYYMM], index)
      }
    } else {
      if (props.selectedYYYYMM == 0){
        emit('go-to-play-photo', infoVue["playList"]["play"]["photo"][props.currentTag], index)
      } else {
        emit('go-to-play-photo', infoVue["playPhoto"][props.selectedYYYYMM], index)
      }
    }
  }
  const goToPlaylist = () => {
    emit('go-to-playlist')
  }
  const changeYYYYMM = (yyyymm: number) => {  // 何年何月が選択されたかを受け取る
    emit('change-yyyymm', yyyymm)
  }
  const selectTag = (tag: string) => {
    emit('select-tag', tag)
  }

  // DOM読み込み時にメニューバーをスクロールさせる
  const cellWidth = 30
  const allWidth = 100
  onMounted(() => {
    const pos = infoVue["yyyymm2pos"][props.selectedYYYYMM]
    let scrollLeft = 0
    if (pos !== -1){
      scrollLeft = allWidth + cellWidth * (pos - 4)
    }
    document.getElementById("nav")!.scrollLeft = scrollLeft
  })

  // 「次の月へ」のリンクをクリック時の処理
  const nextMonth = () => {
    const idx = infoVue["yearMonthList"].indexOf(props.selectedYYYYMM)
    emit('change-yyyymm', infoVue["yearMonthList"][idx + 1])
  }

  // 「前の月へ」のリンクをクリック時の処理
  const previousMonth = () => {
    const idx = infoVue["yearMonthList"].indexOf(props.selectedYYYYMM)
    emit('change-yyyymm', infoVue["yearMonthList"][idx - 1])
  }
</script>

<template>
  <!-- 上部のメニューバー -->
  <Nav :infoGant="infoVue['gant']"
       :yearList="infoVue['yearList']"
       :monthList="infoVue['monthList']"
       :selectedYYYYMM="selectedYYYYMM"
       :cellWidth="cellWidth"
       :allWidth="allWidth"
       @change-yyyymm="changeYYYYMM"
       id="nav"
  />

  <!-- 上部見出し -->
  <div class="wrapper">
    <h1 class="title">
      <span v-if="selectedYYYYMM != 0"> {{infoVue['yyyymm2text'][selectedYYYYMM]}}</span>
      <span v-else-if="currentTag==''"> Playlist</span>
      <span v-else> {{currentTag }} </span>
      <span class="birth-info">
        {{ infoVue["birthText"][selectedYYYYMM] }}
      </span>
      <span v-if="selectedYYYYMM == 0 && currentTag != ''">
          <span class="link" style="float: right;" @click="goToPlaylist"> <u>PlayList へ戻る</u>
          </span>
      </span>
    </h1>

    <Thumb v-if="selectedYYYYMM !=0" 
          :infoThumbMovie="infoVue['thumbMovie'][selectedYYYYMM]"
          :infoThumbPhoto="infoVue['thumbPhoto'][selectedYYYYMM]"
          :selectedYYYYMM="selectedYYYYMM"
          @go-to-play="goToPlay"
          id="thumb"/>
    <PlayList v-if="selectedYYYYMM==0 && currentTag==''" 
          :thumbnail="infoVue['playList']['thumbnail']['all']"
          @select-tag="selectTag"
          id="playlist"/>
    <Thumb v-if="selectedYYYYMM==0 && currentTag!=''"
          :infoThumbMovie="infoVue['playList']['thumbnail']['movie'][currentTag]"
          :infoThumbPhoto="infoVue['playList']['thumbnail']['photo'][currentTag]"
          :selectedYYYYMM="selectedYYYYMM"
          @go-to-play="goToPlay"
          id="thumb"/>
    <!-- 下部のページ移動リンク -->
    <template v-if="selectedYYYYMM !== 0">
      <div class="bottom-link">
        <template v-if="selectedYYYYMM !== infoVue['yearMonthList'][0]">
          <span class="link" @click="previousMonth">
            <u>前の月</u>
          </span>
          ＜
        </template>

        <span class="bottom-yyyymm">
          {{ infoVue['yyyymm2text'][selectedYYYYMM] }}
        </span>

        <template v-if="selectedYYYYMM !== infoVue['yearMonthList'].slice(-1)[0]">
          ＞
          <span class="link" @click="nextMonth">
            <u>次の月</u>
          </span>
        </template>
      </div>
    </template>
  </div>
</template>

<style scoped>
  .bottom-yyyymm{
    color:gray;
    margin-left:6px;
    margin-right:6px;
  }
  .title {
    font-size: 40px;
    margin: 20px 0px;
    padding-left: 0px;
    color: #3a2411;
    max-width: 1100px;
  }
  .birth-info {
    margin-left: 10px;
    font-size: 14px;
  }
  .link {
    font-size: 18px;
    cursor: pointer;
    color: #3a2411;
  }
  .bottom-link{
    text-align:center;
    margin-top: 40px;
    margin-bottom: 40px;
    font-size:16px;
  }
  .wrapper{
    max-width: 1100px;
    margin: 0 auto;
  }
</style>
