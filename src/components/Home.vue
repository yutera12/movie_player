<script setup lang="ts">
  import { onMounted } from 'vue'
  import Nav from './Nav.vue'
  import Thumb from './Thumb.vue'
  import axios from 'axios'

  //////////////////////////
  // info_vue.jsonの読み込み //
  //////////////////////////
  type InfoVue = {
    yearMonthList: number[],
    yearList: number[],
    monthList: number[][]
    birthText: {[key in number]: string}
    infoGant: {"name": string; "gant": {[key in string]: number[]}}[]
    yyyymm2pos: {[key in number]: number}
    yyyymm2text: {[key in number]: string}
    infoThumbPhoto: {[key in number]: {fileName: string; id: number; date: string; aspectRatio: number;}[]}
    infoPlayPhoto: {[key in number]:{fileName: string; date: string; id: number;}[]}
    infoPlayMovie: {[key in number]: {totalTime: number[]; fileName: string[]; id: number;}[]}
    infoThumbMovie: {[key in number]: {fileName: string; id: number; totalTime: string; date: string; aspectRatio: number;}[]}
  }
  let infoVue:InfoVue = {"yearMonthList": [], "yearList": [], "monthList": [[]],
  "birthText": {0: ""}, "infoGant":[], "yyyymm2pos":{}, "yyyymm2text":{}, "infoThumbPhoto": {}, "infoPlayPhoto": {},
  "infoPlayMovie": {}, "infoThumbMovie": {}}
  await axios.get("images/info_vue.json").then(function(response) {
    infoVue = response.data
  })
  const yyyymm2pos:{[key in number]: number} = infoVue["yyyymm2pos"]
  const birthText = infoVue["birthText"]
  const infoGant = infoVue["infoGant"]

  // App.vueから情報を受けとり
  const props = defineProps<{
    selectedYYYYMM: number
  }>();

  // App.vueで定義されるイベントを発火
  const emit = defineEmits(['go-to-play-movie', 'go-to-play-photo', 'change-yyyymm'])
  const goToPlay = (id: number, isMovie:boolean) => { // 何番目のサムネイルをクリックしたかを受け取る
    if (isMovie){
      emit('go-to-play-movie', infoVue["infoPlayMovie"][props.selectedYYYYMM], id, props.selectedYYYYMM === 0)
    } else {
      emit('go-to-play-photo', infoVue["infoPlayPhoto"][props.selectedYYYYMM], id)
    }
  }
  const changeYYYYMM = (yyyymm: number) => {  // 何年何月が選択されたかを受け取る
    emit('change-yyyymm', yyyymm)
  }

  // DOM読み込み時にメニューバーをスクロールさせる
  const cellWidth = 40
  const allWidth = 60
  onMounted(() => {
    const pos = yyyymm2pos[props.selectedYYYYMM]
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
  <Nav :infoGant="infoGant"
       :yearList="infoVue['yearList']"
       :monthList="infoVue['monthList']"
       :selectedYYYYMM="selectedYYYYMM"
       :cellWidth="cellWidth"
       :allWidth="allWidth"
       @change-yyyymm="changeYYYYMM"
       id="nav"
  />

  <!-- 上部見出し -->
  <h1 v-if="selectedYYYYMM != 0" class="title">
    <span class="text">
      {{infoVue['yyyymm2text'][selectedYYYYMM]}}
    </span>
    <span class="birth-info">
      {{ birthText[selectedYYYYMM] }}
    </span>
  </h1>
  <h1 v-else class="title">
    <span class="text">まとめ</span>
  </h1>
  <!-- サムネイル -->
  <Thumb :infoThumbMovie="infoVue['infoThumbMovie'][selectedYYYYMM]"
         :infoThumbPhoto="infoVue['infoThumbPhoto'][selectedYYYYMM]"
         :selectedYYYYMM="selectedYYYYMM"
         @go-to-play="goToPlay"
         id="thumb"/>

  <!-- 下部のページ移動リンク -->
  <template v-if="selectedYYYYMM !== 0">
    <div class="bottom-link">
      <template v-if="selectedYYYYMM !== infoVue['yearMonthList'][0]">
        <span class="link" @click="previousMonth">
          <u >前の月</u>
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
</template>

<style scoped>
  .bottom-yyyymm{
    color:gray;
    margin-left:6px;
    margin-right:6px;
  }
  .title {
    font-size: 40px;
    margin-bottom: 20px;
    color: #3a2411;
    max-width: 1100px;
    margin: 20px auto;
  }
  .text {
    margin-left: 10px;
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
</style>
