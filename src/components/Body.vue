<script setup lang="ts">

  import { ref, reactive, onActivated } from 'vue'
  import axios from 'axios'

  type Time = {
    min: number;
    sec: number;
  }
  type InfoPlay = {
    time1: number;
    time2: number;
    fileName: string;
  }
  type InfoData = {
    time1: number;
    time2: number;
    fileName: string;
    comment: string;
    date: number;
    thumbnailTime: Time;
  }
  type InfoAll = {
    title: string;
    data: InfoData[];
  }[]

  // min, sec -> sec
  const ms2s = (time:Time) => {
    return time.min * 60 + time.sec
  }
  // 動画の再生時間を返す
  const retTotalTime = (time1:number, time2:number) => {
    const totalTime = time2 - time1
    if(totalTime > 59.5){
      const m = Math.floor(Math.round(totalTime) / 60)
      const s = Math.round(totalTime - m * 60)
      return m + "分" + s + "秒"
    } else {
      return Math.round(totalTime) + "秒"
    }
  }
  // yyyymmddをyyyy年mm月dd日にして返す
  const parseDate = (yyyymmdd:number) => {
    if (yyyymmdd === 0){
      return ""
    }
    const yyyy = Math.floor(yyyymmdd / 10000);
    const mmdd = yyyymmdd - yyyy * 10000;
    const mm = Math.floor(mmdd / 100);
    const dd = mmdd - mm * 100
    return yyyy + "年" + mm + "月" + dd + "日"
  }

  // info.jsonからの読み込み
  const infoAll:InfoAll = reactive([])
  axios.get("images/info.json").then(function(response) {
    for (const v of response.data){
      const title:string = v.title
      const infoData:InfoData[] = []
      for (const d of v.data){
        infoData.push({
          fileName: d.fileName,
          time1: ms2s({min:d.playTime[0][0] ,sec:d.playTime[0][1]}),
          time2: ms2s({min:d.playTime[1][0] ,sec:d.playTime[1][1]}),
          comment: d.comment,
          date: d.date,
          thumbnailTime: {min: d.thumbnailTime[0], sec: d.thumbnailTime[1]},
        })
      }
      infoAll.push({title: title, data: infoData});
    }
  })

  // play画面への移動
  let anchor = ref("")  // home画面に戻ってきた時のためにスクロール先を保持
  const emit = defineEmits(['change-page'])
  const changePage = (time1: number, time2: number, fileName: string, title:string) => {
    let info: InfoPlay = {time1, time2, fileName}
    anchor.value = title
    emit('change-page', info)
  }

  // スクロール
  let firstTime = ref(true)  // home画面を表示するのが最初か否か
  onActivated(() => {
    if (firstTime.value){ // home画面の初回表示時はスクロールしない
      firstTime.value = false
    } else { // home画面の2回目以降の表示時はスクロール
      const element = document.getElementById(anchor.value)!
      const rect = element.getBoundingClientRect();
      const elemtop = rect.top + window.pageYOffset
      document.documentElement.scrollTop = elemtop
    }
  })
</script>

<template>
  <main class="pt-3 mb-2 bg-light">
    <div class="container-fluid">
      <div v-for="value in infoAll" :key="value.title">
        <div class="row pt-5">
          <h1 :id="value.title">{{ value.title }}</h1>
          <template v-for="x in value.data" :key="value.data.fileName">
            <div class="col-sm-6 col-md-4 col-lg-3 pt-3">
              <div class="card box-shadow">
                <div class="card-img-top" @click="changePage(x.time1, x.time2, x.fileName, value.title)">
                  <img :src="'images/thumbnails/' + x.fileName + '__' + ms2s(x.thumbnailTime) +'.png'"
                        style="width:100%"
                        class="img-thumbnail"
                  >
                </div>
                <div class="card-body">
                  <div class="card-text">{{x.comment}}</div>
                  <div class="small test-right" style="text-align: right">
                    {{retTotalTime(x.time1, x.time2)}}&nbsp;&nbsp;{{parseDate(x.date)}}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
  .card-img-top {
    position: relative;
    cursor: pointer;
  }
  .card-img-top .icon {
    position: absolute;
    top: 50%;
    left: 50%;
    -ms-transform: translate(-50%, -50%);
    -webkit-transform: translate(-50%, -50%);
    transform: translate(-50%, -50%);
    margin: 0;
    padding: 0;
  }
</style>