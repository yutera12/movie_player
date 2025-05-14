<script setup lang="ts">

  import { ref, onMounted } from 'vue'

  // 型情報
  type InfoPlayMovie = {
    totalTime: number;
    fileName: string;
    id: number;
  }[]

  // 少数第2位を四捨五入
  const format = (val:number) => {
    return Math.round(val * 10) / 10
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
  let info = ref(true)
  let filePaths:string[] = []
  let totalTime:number[] = []
  props.infoPlayMovie.forEach(function(d, i){
      filePaths.push(d.fileName)
      totalTime.push(d.totalTime)
  })
  let tooltip = ref({
    "home1": false,
    "home2": false
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
  })

  // home
  const toHome = () => {
    document.exitFullscreen()
    goToHome()
  }

  // 進む
  const proceed = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    if (ind.value + 1 < filePaths.length){
      ind.value += 1
      setTimeout(function(){
        videoElem.play()
      }, 100);
    }
  }

  // 戻る
  const back = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    if (videoElem.currentTime < 1){
      if (ind.value != 0){
        ind.value -= 1
      }
    }
    videoElem.load()
    setTimeout(function(){
        videoElem.play()
      }, 100);
  }

  const mover = (key: "home1" | "home2") => {
      tooltip.value[key] = true
  }
  const mleave = (key: "home1" | "home2") => {
    tooltip.value[key] = false
  }
  const change_info = () => {
    if (info.value) {
      info.value = false
    } else {
      info.value = true
    }
  }
  document.body.addEventListener("keydown",
    event => {
      if (event.key == "ArrowUp") {
        toHome()
      }
      else if (event.key == "ArrowLeft") {
        back()
      }
      else if (event.key == "ArrowRight") {
        proceed()
      }
      else if (event.key == "i") {
        change_info()
      }
    }
  )
</script>

<template>
  <video controls autoplay
    id="video"
    controlslist="nodownload"
    oncontextmenu="return false"
    :src="filePaths[ind]"
    preload="metadata"
    style="position: absolute; width:100%; height: 100%; z-index:-100; background: black"
  ></video>
  <template v-if="info == true">
    <div class="tooltip" style="left: 5px" v-if="tooltip['home1'] || tooltip['home2'] ">ホーム画面に戻る(↑)</div>
    <div class="circle" style="left: 5px;"  @click="toHome()" @mouseover="mover('home1')" @mouseleave="mleave('home1')"></div>
    <img src="/images/icon/home.png" class="icon" style="left: 10px;" @click="toHome()" @mouseover="mover('home2')" @mouseleave="mleave('home2')">
  </template>
</template>

<style scoped>
.circle{
  width: 40px;
  height: 40px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  top: 5px;
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
  top: 10px;
  cursor: pointer;
}

.tooltip{
  top: 50px;
  padding: 2px;
  position: absolute;
  border: solid 0.5px #3a2411;
  background: #f1eac3;
}
</style>