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
  }
  let infoVue:InfoVue = {"yearMonthList": [], "yearList": [], "monthList": [[]], "birthText": {0: ""}, "infoGant":[], "yyyymm2pos":{}, "yyyymm2text":{}}
  await axios.get("images/info_vue.json").then(function(response) {
    infoVue = response.data
  })
  const yyyymm2pos:{[key in number]: number} = infoVue["yyyymm2pos"]

  //////////////////////////
  // info.jsonの読み込み //
  //////////////////////////
  type ShortData = {
    fileName: string;
    totalTime: number;
    totalTimeThumb: string;
    yyyymm: number;
    date: string;
    aspectRatio: number;
    thumbnailFile: string;
  }[]
  let shortData:ShortData = []

  type LongData = {
    fileName: string[];
    totalTime: number[];
    totalTimeThumb: string;
    date: string;
    thumbnailFile: string;
    aspectRatio: number;
  }[]
  let longData:LongData = []

  type PhotoData = {
    fileName: string;
    thumbnailFile: string;
    date: string;
    yyyymm: number;
    aspectRatio: number;
  }[]
  let photoData:PhotoData = []

  type Data = {
    short: ShortData,
    long: LongData,
    photo: PhotoData,
  }
  let data:Data = {"short": [], "long": [], "photo": []}

  await axios.get("images/info.json").then(function(response) {
    data = response.data
  })
  shortData = data["short"]
  longData = data["long"]
  photoData = data["photo"]

  ///////////////////////////////////////////////////////////////
  // 動画・写真の再生＆サムネイル表示に必要な情報を格納する箱の定義 //
  ///////////////////////////////////////////////////////////////
  type InfoPlayMovie = {
    [key in number]: {  // keyはyyyymm
      totalTime: number[];
      fileName: string[];
      id: number;
    }[]
  }
  type InfoPlayPhoto = {
    [key in number]: {  // keyはyyyymm
      fileName: string;
      date: string;
      id: number;
    }[]
  }
  type InfoThumbMovie = {
    [key in number]: {  // keyはyyyymm
      fileName: string;
      id: number;
      totalTime: string;
      date: string;
      aspectRatio: number;
    }[]
  }
  type InfoThumbPhoto = {
    [key in number]: {  // keyはyyyymm
      fileName: string;
      id: number;
      date: string;
      aspectRatio: number;
    }[]
  }

  const infoPlayMovie: InfoPlayMovie = {}
  const infoPlayPhoto: InfoPlayPhoto = {}
  const infoThumbMovie: InfoThumbMovie = {}
  const infoThumbPhoto: InfoThumbPhoto = {}
  infoPlayMovie[0] = []
  infoPlayPhoto[0] = []
  infoThumbMovie[0] = []
  infoThumbPhoto[0] = []
  infoVue["yearMonthList"].forEach(function(yyyymm, i){
    infoPlayMovie[yyyymm] = []
    infoPlayPhoto[yyyymm] = []
    infoThumbMovie[yyyymm] = []
    infoThumbPhoto[yyyymm] = []
  })

  let id_movie = 0
  let id_photo = 0

  // short
  shortData.forEach(function(d, i){

    // infoThumbMovie作成 //
    infoThumbMovie[d.yyyymm].push(
      {
        fileName: d.thumbnailFile,
        id: id_movie,
        totalTime: d.totalTimeThumb,
        date: d.date,
        aspectRatio: d.aspectRatio
      }
    )
    // infoPlayMovie作成 //
    infoPlayMovie[d.yyyymm].push(
      {
        fileName: [d.fileName],
        totalTime: [d.totalTime],
        id: id_movie
      }
    )
    id_movie += 1
  })

  // long
  longData.forEach(function(d, i){
    const yyyymm = 0
    infoThumbMovie[yyyymm].push(
      {
        fileName: d.thumbnailFile,
        id: id_movie,
        totalTime: d.totalTimeThumb,
        date: d.date,
        aspectRatio: d.aspectRatio
      }
    )

    infoPlayMovie[0].push(
      {
        fileName: d.fileName,
        totalTime: d.totalTime,
        id: id_movie
      }
    )

    id_movie += 1
  })

  photoData.forEach(function(d, i){

    // infoThumbPhoto作成 //
    infoThumbPhoto[d.yyyymm].push(
      {
        fileName: d.thumbnailFile,
        id: id_photo,
        date: d.date,
        aspectRatio: d.aspectRatio
      }
    )

    // infoPlayPhoto作成 //
    infoPlayPhoto[d.yyyymm].push({
      fileName: d.fileName,
      date: d.date,
      id: id_photo
    })

    infoPlayPhoto[0].push({
      fileName: d.fileName,
      date: d.date,
      id: id_photo
    })

    id_photo += 1
  })

  //////////////////////////////////////////////////////////////////
  // birthTextList(「a：0歳8ヵ月～0歳9ヵ月、b：誕生前」の表示に必要) //
  /////////////////////////////////////////////////////////////////
  const birthText = infoVue["birthText"]

  //////////////////
  // infoGant作成 //
  //////////////////
  type InfoGant = {
    "name": string;
    "gant": {[key in string]: number[]}
  }[]
  const infoGant = infoVue["infoGant"]
  // App.vueから情報を受けとり
  const props = defineProps<{
    selectedYYYYMM: number
  }>();

  // App.vueで定義されるイベントを発火
  const emit = defineEmits(['go-to-play-movie', 'go-to-play-photo', 'change-yyyymm'])
  const goToPlay = (id: number, isMovie:boolean) => { // 何番目のサムネイルをクリックしたかを受け取る
    if (isMovie){
      emit('go-to-play-movie', infoPlayMovie[props.selectedYYYYMM], id, props.selectedYYYYMM === 0)
    } else {
      emit('go-to-play-photo', infoPlayPhoto[props.selectedYYYYMM], id)
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
  <Thumb :infoThumbMovie="infoThumbMovie[selectedYYYYMM]"
         :infoThumbPhoto="infoThumbPhoto[selectedYYYYMM]"
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
