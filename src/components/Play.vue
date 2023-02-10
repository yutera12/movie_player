<script setup lang="ts">

  import { ref, onMounted } from 'vue'

  // 型情報
  type InfoPlayMovie = {
    totalTime: number;
    fileName: string;
  }[]

  // 少数第2位を四捨五入
  const format = (val:number) => {
    return Math.round(val * 10) / 10
  }

  // long動画において、現在の再生時間を返す
  const retCurrentTimeLong = (currentTime:number, index:number, totalTime:number[]) => {
    let addTime = 0
    if (index !== 0){
      addTime = totalTime.slice(0, index).reduce(function(sum, element){return sum + element;}, 0)
    }
    return currentTime + addTime
  }
  // long動画において、総再生時間を返す
  const retTotalTimeLong = (totalTime: number[]) => {
    return totalTime.reduce(function(sum, element){return sum + element;}, 0)
  }

  // App.vueのイベントを発火
  const emit = defineEmits(['go-to-home'])
  const goToHome = () => {
    emit('go-to-home')
  }

  // App.vueから情報を受けとり、初期値を設定
  const props = defineProps<{
    infoPlayMovie:InfoPlayMovie
    isLong: boolean
    index: number
  }>();
  let ind = ref(props.index)
  let filePaths:string[] = []
  let totalTime:number[] = []
  props.infoPlayMovie.forEach(function(d, i){
      filePaths.push(d.fileName)
      totalTime.push(d.totalTime)
  })
  let currentTime = ref(0)  // 現在の再生時間

  // DOM読み込み後に実行
  onMounted(() => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    videoElem.addEventListener('timeupdate', function() {
      currentTime.value = format(videoElem.currentTime)
    })

    if(props.isLong){
      // 終了したら次のチャプターへ移動し自動再生
      videoElem.addEventListener('ended', (event) => {
        if (ind.value + 1 < filePaths.length){
          ind.value += 1
          setTimeout(function(){videoElem.play()},1000);
        }
      })
    }
    document.documentElement.requestFullscreen();
    videoElem.play()
  })

  // 停止・再生の制御
  const pause_or_play = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    if (videoElem.paused) {  // 停止中
      videoElem.play()
    } else {  // 再生中
      videoElem.pause()
    }
  }

  // homeボタン
  const toMenu = () => {
    document.exitFullscreen()
    goToHome()
  }

  // スキップボタン
  const skipSecond = (s: number) => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    videoElem.currentTime = Math.min(Math.max(videoElem.currentTime + s, 0), totalTime[props.index])
  }

  // 進むボタン
  const proceed = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    if (ind.value + 1 < filePaths.length){
      ind.value += 1
      videoElem.currentTime = 0
      setTimeout(function(){
        videoElem.play()
      }, 100);
    }
  }

  // 戻るボタン
  const back = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    if (videoElem.currentTime < 1){
      if(ind.value != 0){
        ind.value -= 1
        setTimeout(function(){
          videoElem.play()
        }, 100);
      }
    }
    videoElem.currentTime = 0
  }

</script>

<template>
  <video
    id="video"
    controlslist="nodownload"
    oncontextmenu="return false"
    :src="filePaths[ind]"
    preload="metadata"
    style="position: absolute; width:100%; height: 100%; z-index:-100; background: black"
    @click="pause_or_play()"
  ></video>
  <div class="circle" style="left: 5px;"  @click="toMenu()"></div>
  <div class="circle" style="left: 59px;" @click="skipSecond(-5)"></div>
  <div class="circle" style="left: 113px;" @click="skipSecond(10)"></div>
  <div class="circle" style="left: 167px;" @click="back()"></div>
  <div v-if="filePaths.length > 1" class="circle" style="left: 221px;" @click="proceed()"></div>
  <img src="/images/icon/home.png" class="icon" style="left: 8px;" @click="toMenu()">
  <div class="changeTime" style="left: 74px;" @click="skipSecond(-5)">-5</div>
  <div class="changeTime" style="left: 116px;" @click="skipSecond(10)">+10</div>
  <img src="/images/icon/leftarrow.png" class="icon" style="left: 168px;" @click="back()">
  <img v-if="filePaths.length > 1" src="/images/icon/rightarrow.png" class="icon" style="left: 222px;" @click="proceed()">
  <div style="position: absolute; bottom: 5px; right: 20px; font-size: 25px; color: rgb(255,255,255,0.5)">
    <span v-if="props.isLong"> {{format(retCurrentTimeLong(currentTime, ind, totalTime))}}/{{ format(retTotalTimeLong(totalTime)) }}秒, {{ind + 1}}/{{filePaths.length}}チャプタ</span>
    <span v-else>{{currentTime}}/{{format(totalTime[ind])}}秒</span>
  </div>
</template>

<style scoped>
.circle{
  width: 50px;
  height: 50px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  bottom: 5px;
  cursor: pointer;
}
.changeTime{
  position: absolute;
  bottom: 17px;
  font-size: 25px;
  cursor: pointer;
  color: #303030
}
.icon{
  width: 45px;
  height: 45px;
  position: absolute;
  bottom: 8px;
  cursor: pointer;
}
</style>