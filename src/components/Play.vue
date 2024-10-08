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
    index: number
  }>();
  let ind = ref(props.index)
  let filePaths:string[] = []
  let totalTime:number[] = []
  props.infoPlayMovie.forEach(function(d, i){
      filePaths.push(d.fileName)
      totalTime.push(d.totalTime)
  })
  let tooltip = ref({
    "home1": false,
    "home2": false,
    "skip_plus1": false,
    "skip_plus2": false,
    "skip_minus1": false,
    "skip_minus2": false,
    "proceed1": false,
    "proceed2": false,
    "back1": false,
    "back2": false
  })
  let currentTime = ref(0)  // 現在の再生時間

  // DOM読み込み後に実行
  onMounted(() => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    videoElem.addEventListener('timeupdate', function() {
      currentTime.value = format(videoElem.currentTime)
    })

    // 終了したら次のチャプターへ移動し自動再生
    videoElem.addEventListener('ended', (event) => {
      if (ind.value + 1 < filePaths.length){
        ind.value += 1
        setTimeout(function(){videoElem.play()}, 1000);
      }
    })

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
    videoElem.currentTime = Math.min(Math.max(videoElem.currentTime + s, 0), totalTime[ind.value])
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

  const mover = (key: "home1" | "skip_plus1" | "skip_minus1" | "proceed1" | "back1" | "home2" | "skip_plus2" | "skip_minus2" | "proceed2" | "back2") => {
    tooltip.value[key] = true
  }
  const mleave = (key: "home1" | "skip_plus1" | "skip_minus1" | "proceed1" | "back1" | "home2" | "skip_plus2" | "skip_minus2" | "proceed2" | "back2") => {
    tooltip.value[key] = false
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
  <div class="tooltip" style="left: 5px" v-if="tooltip['home1'] || tooltip['home2'] ">ホームに戻る</div>
  <div class="tooltip" style="left: 49px" v-if="tooltip['skip_minus1'] || tooltip['skip_minus2']">5秒戻る</div>
  <div class="tooltip" style="left: 93px" v-if="tooltip['skip_plus1'] || tooltip['skip_plus2']">10秒進む</div>
  <div class="tooltip" style="left: 137px" v-if="tooltip['back1'] || tooltip['back2']">前へ戻る</div>
  <div class="tooltip" style="left: 186px" v-if="tooltip['proceed1'] || tooltip['proceed2']">次へ進む</div>

  <div class="circle" style="left: 5px;"  @click="toMenu()" @mouseover="mover('home1')" @mouseleave="mleave('home1')"></div>
  <div class="circle" style="left: 49px;" @click="skipSecond(-5)" @mouseover="mover('skip_minus1')" @mouseleave="mleave('skip_minus1')"></div>
  <div class="circle" style="left: 93px;" @click="skipSecond(10)" @mouseover="mover('skip_plus1')" @mouseleave="mleave('skip_plus1')"></div>
  <div class="circle" style="left: 137px;" @click="back()" @mouseover="mover('back1')" @mouseleave="mleave('back1')"></div>
  <div v-if="filePaths.length > 1" class="circle" style="left: 181px;" @click="proceed()" @mouseover="mover('proceed1')" @mouseleave="mleave('proceed1')"></div>

  <img src="/images/icon/home.png" class="icon" style="left: 10px;" @click="toMenu()" @mouseover="mover('home2')" @mouseleave="mleave('home2')">
  <div class="changeTime" style="left: 62px;" @click="skipSecond(-5)" @mouseover="mover('skip_minus2')" @mouseleave="mleave('skip_minus2')">-5</div>
  <div class="changeTime" style="left: 93px;" @click="skipSecond(10)"  @mouseover="mover('skip_plus2')" @mouseleave="mleave('skip_plus2')">+10</div>
  <img src="/images/icon/leftarrow.png" class="icon" style="left: 141px;" @click="back()" @mouseover="mover('back2')" @mouseleave="mleave('back2')">
  <img v-if="filePaths.length > 1" src="/images/icon/rightarrow.png" class="icon" style="left: 186px;" @click="proceed()" @mouseover="mover('proceed2')" @mouseleave="mleave('proceed2')">

  <div style="position: absolute; bottom: 5px; right: 20px; font-size: 20px; color: rgb(255,255,255,0.5)">
    <!-- <span v-if="props.is"> {{format(retCurrentTimeLong(currentTime, ind, totalTime))}}/{{ format(retTotalTimeLong(totalTime)) }}秒, {{ind + 1}}/{{filePaths.length}}チャプタ</span> -->
    <!-- <span v-else>{{currentTime}}/{{format(totalTime[ind])}}秒</span> -->
    <span>{{currentTime}}/{{format(totalTime[ind])}}秒</span>
  </div>
</template>

<style scoped>
.circle{
  width: 40px;
  height: 40px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  bottom: 5px;
  cursor: pointer;
}
.changeTime{
  position: absolute;
  bottom: 13px;
  font-size: 22px;
  cursor: pointer;
  color: #303030
}
.icon{
  width: 30px;
  height: 30px;
  position: absolute;
  bottom: 10px;
  cursor: pointer;
}

.tooltip{
  bottom: 50px;
  padding: 2px;
  position: absolute;
  border: solid 0.5px #3a2411;
  background: #f1eac3;
}
</style>