<script setup lang="ts">
  import { onMounted } from 'vue'
  import Nav from './Nav.vue'
  import Thumb from './Thumb.vue'
  import axios from 'axios'

  /////////////////
  // 各種メソッド //
  /////////////////
  const parse_yyyymm = (yyyymm: number) => {
    const year = Math.floor(yyyymm / 100)
    const month = yyyymm - year * 100
    return String(year) + "年" + String(month) + "月"
  }

  const yyyymmdd2pos = (yyyymmdd:number, yearList:number[], monthList:number[][]) => {
    /*
    yyyymmddを入力すると、home画面上部の月のリストのどの位置に相当するかを返す

    例
    yearList : [2020, 2021]
    monthList : [[10, 12], [1, 2]]

    yyyymmdd | return
    -------- | -----
    0        | -1     # 0が入力されたら-1を返す
    20200910 | 0      # 2020/09/10は2000/10の箱（一つ目の箱）よりも前なので0
    20201010 | 0.333  # 2020/10/10は2000/10の箱の中の1/3の位置に相当するので、1/3
    20201110 | 1      # 2020/11/10は2000/10の箱と2020/12の箱の間に相当するので1
    20201210 | 1.333
    20210110 | 2.333
    20210210 | 3.333
    20210310 | -1     # 2021/03/10は最後の箱(2021/2の箱)の外側に相当するので-1
    */
    if (yyyymmdd === 0){
      return -1
    }
    const yyyymm = Math.floor(yyyymmdd / 100)
    const dd = yyyymmdd - yyyymm * 100
    let pos = 0
    for (let i = 0; i < yearList.length; i++) {
      const year = yearList[i]
      for (let j = 0; j < monthList[i].length; j++){
        const month = monthList[i][j]
        if (year * 100 + month === yyyymm){
          return pos + dd / 30
        } else if (year * 100 + month > yyyymm) {
          return pos
        }
        pos += 1
      }
    }
    return -1
  }

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

  type InfoThumbData = {
    [key in string]: number[] // key: ファイル名, value: サムネイルの時間 ([分, 秒])
  }
  let infoThumbData:InfoThumbData = {}

  type LongData = {
    fileName: string[];
    totalTime: number[];
    totalTimeThumb: string;
    date: string;
    thumbnailFile: string;
    aspectRatio: number;
  }[]
  let longData:LongData = []

  type BirthData = {
    name: string;
    date: number;
  }[]
  let birthData:BirthData = []

  type PhotoData = {
    fileName: string;
    thumbnailFile: string;
    date: string;
    yyyymm: number;
    aspectRatio: number;
  }[]
  let photoData:PhotoData = []

  type Data = {
    birth: BirthData,
    short: ShortData,
    long: LongData,
    photo: PhotoData,
  }
  let data:Data = {"birth": [], "short": [], "long": [], "photo": []}

  await axios.get("images/info.json").then(function(response) {
    data = response.data
  })
  shortData = data["short"]
  longData = data["long"]
  birthData = data["birth"]
  photoData = data["photo"]

  ////////////////////////////////////////////
  // yearList, monthList, yearMonthList作成 //
  ////////////////////////////////////////////
  //    例
  //    yearMonthList : [200010, 200012, 200101, 200102]
  //    yearList : [2000, 2001]
  //    monthList : [[10, 12], [1, 2]]
  let yearList:number[] = []
  let monthList:number[][] = [[]]
  let yearMonthList:number[] = []
  shortData.forEach(function(d, i){
    yearMonthList.push(d.yyyymm)
  })
  photoData.forEach(function(d, i){
    yearMonthList.push(d.yyyymm)
  })
  yearMonthList = Array.from(new Set(yearMonthList)).sort()
  for (const yyyymm of yearMonthList){
    yearList.push(Math.floor(yyyymm / 100))
  }
  yearList = Array.from(new Set(yearList)).sort()

  for (let i = 0; i < yearList.length - 1; i++){
    monthList.push([])
  }
  for (const yyyymm of yearMonthList){
    const year = Math.floor(yyyymm / 100)
    const month = yyyymm - 100 * year
    const idx = yearList.indexOf(year)
    monthList[idx].push(month)
  }

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
  yearMonthList.forEach(function(yyyymm, i){
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

    const f:string[] = []
    d.fileName.forEach(function(d, i){
      f.push(d)
    })
    infoPlayMovie[0].push(
      {
        fileName: f,
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
  type BirthText = {
    [key in number]: string  // keyはyyyymm, valueは生後の期間情報
  }
  const birthText:BirthText = {}
  for (const yyyymm of yearMonthList){
    const year = Math.floor(yyyymm / 100)
    const month = yyyymm - year * 100
    let txt = ""
    birthData.forEach(function(d){
      const name = d.name
      const birthYYYYMM = Math.floor(d.date / 100)
      const birthYYYY = Math.floor(birthYYYYMM / 100)
      const birthMM = birthYYYYMM - birthYYYY * 100
      const yyyymm = year * 100 + month
      if (yyyymm < birthYYYYMM){
        txt += name + "：誕生前、"
      }
      if (yyyymm === birthYYYYMM){
        txt += name + "：誕生前～0歳0ヵ月、"
      }
      if (yyyymm > birthYYYYMM){
        const yyyy = Math.floor(yyyymm / 100)
        const mm = yyyymm - yyyy * 100
        const diffMonth1 = (yyyy - birthYYYY) * 12 + (mm - birthMM) - 1
        const diffMonth2 = diffMonth1 + 1
        const ageY1 = Math.floor(diffMonth1 / 12)
        const ageM1 = diffMonth1 - ageY1 * 12
        const ageY2 = Math.floor(diffMonth2 / 12)
        const ageM2 = diffMonth2 - ageY2 * 12
        txt += name + "：" + ageY1 + "歳" + ageM1 + "ヵ月"
        txt += "～" + ageY2 + "歳" + ageM2 + "ヵ月、"
      }
    })
    birthText[yyyymm] = txt.slice(0, -1)
  }

  //////////////////
  // infoGant作成 //
  //////////////////
  type InfoGant = {
    "name": string;
    "gant": {[key in string]: number[]}
  }[]
  const infoGant:InfoGant = []
  birthData.forEach( function(v){
    const birthday = v.date
    const info:{[key in string]: number[]} = {}
    let age = -1
    while ( true ) {
      age += 1
      const x1 = birthday + 10000 * age
      const x2 = birthday + 10000 * (age + 1)
      if (x1 > yearList.slice(-1)[0] * 10000 + monthList.slice(-1)[0].slice(-1)[0] * 100){
        break
      }
      const x1_pos = yyyymmdd2pos(x1, yearList, monthList)
      const x2_pos = yyyymmdd2pos(x2, yearList, monthList)
      if (x1_pos === 0 && x2_pos === 0){
        continue
      }
      info[`${v.name} ${age}歳`] = [x1_pos, x2_pos]
    }
    infoGant.push({name: v.name, gant: info})
  })

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
    const pos = yyyymmdd2pos(props.selectedYYYYMM * 100, yearList, monthList)
    let scrollLeft = 0
    if (pos !== -1){
      scrollLeft = allWidth + cellWidth * (pos - 4)
    }
    document.getElementById("nav")!.scrollLeft = scrollLeft
  })

  // 「次の月へ」のリンクをクリック時の処理
  const nextMonth = () => {
    const idx = yearMonthList.indexOf(props.selectedYYYYMM)
    emit('change-yyyymm', yearMonthList[idx + 1])
  }

  // 「前の月へ」のリンクをクリック時の処理
  const previousMonth = () => {
    const idx = yearMonthList.indexOf(props.selectedYYYYMM)
    emit('change-yyyymm', yearMonthList[idx - 1])
  }

</script>

<template>
  <!-- 上部のメニューバー -->
  <Nav :infoGant="infoGant"
       :yearList="yearList"
       :monthList="monthList"
       :selectedYYYYMM="selectedYYYYMM"
       :cellWidth="cellWidth"
       :allWidth="allWidth"
       @change-yyyymm="changeYYYYMM"
       id="nav"
  />

  <!-- 上部見出し -->
  <h1 v-if="selectedYYYYMM != 0" class="title">
    <span class="text">
      {{parse_yyyymm(selectedYYYYMM)}}
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
      <template v-if="selectedYYYYMM !== yearList[0] * 100 + monthList[0][0]">
        <span class="link" @click="previousMonth">
          <u >前の月</u>
        </span>
        ＜
      </template>

      <span class="bottom-yyyymm">
        {{ parse_yyyymm(selectedYYYYMM) }}
      </span>

      <template v-if="selectedYYYYMM !== yearList.slice(-1)[0] * 100 + monthList.slice(-1)[0].slice(-1)[0]">
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
