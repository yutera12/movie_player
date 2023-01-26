<script setup lang="ts">

  import { ref, onMounted } from 'vue'

  type Info_p = {
    time1: number;
    time2: number;
    fileName: string;
  }

  // 少数第2位を四捨五入
  const format = (val:number) => {
    return Math.round(val * 10) / 10
  }

  // home画面への移動
  const emit = defineEmits(['change-page'])
  const changePage = () => {
    emit('change-page')
  }

  // home画面からの情報を受けとり
  const props = defineProps<{
    info_p:Info_p
  }>();
  const filePath = 'images/movies/' + props.info_p.fileName + "#t=" + props.info_p.time1 + "," + props.info_p.time2
  const allTime = ref(format(props.info_p.time2 - props.info_p.time1))

  // playerの制御に使用する変数
  let currentTime = ref(0)  // 現在の再生時間
  let reset = ref(true)  // 次回に再生した時に再生時間位置を元に戻す

  onMounted(() => {
    // EventListenerを登録
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    videoElem.addEventListener('timeupdate', function() {
      currentTime.value = format(videoElem.currentTime - props.info_p.time1)

      // 再生時間が終わりを超えた場合は、time2を表示、かつ、停止する。次回の再生位置を初期化する
      if (videoElem.currentTime >= props.info_p.time2){
        currentTime.value = format(props.info_p.time2 - props.info_p.time1)
        videoElem.pause()
        reset.value = true
      } else {
        reset.value = false
      }
    })
  })

  // 停止・再生の制御
  const pause_or_play = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video')!
    if (videoElem.paused) {  // 停止中
      if (reset.value){
        currentTime.value = format(props.info_p.time1)
        videoElem.currentTime = currentTime.value
      }
      const ele = document.documentElement;
      ele.requestFullscreen();
      videoElem.play()
    } else {  // 再生中
      videoElem.pause()
    }
  }

  // 10秒スキップの制御
  const proceed = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    videoElem.currentTime = Math.min(videoElem.currentTime + 10, props.info_p.time2)
  }

  // 5秒戻しの制御
  const back = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    videoElem.currentTime = Math.max(videoElem.currentTime - 5, props.info_p.time1)
  }

  // home画面へ戻る
  const toMenu = () => {
    document.exitFullscreen()
    changePage()
  }

  // 最初から再生
  const reload = () => {
    const videoElem = <HTMLMediaElement>document.getElementById('video');
    videoElem.currentTime = props.info_p.time1
  }

</script>

<template>
  <video
    id="video"
    controlslist="nodownload"
    oncontextmenu="return false"
    :src="filePath"
    preload="metadata"
    style="position: absolute; width:100%; height: 100%; z-index:-100; background: black"
    @click="pause_or_play()"
  ></video>
  <div
    style="width: 50px; height: 50px; border-radius:50%; background: rgb(255,255,255,0.5); position: absolute; bottom: 5px; left: 5px;"
  ></div>
  <div
    style="width: 50px; height: 50px; border-radius:50%; background: rgb(255,255,255,0.5); position: absolute; bottom: 5px; left: 59px;"
  ></div>
  <div
    style="width: 50px; height: 50px; border-radius:50%; background: rgb(255,255,255,0.5); position: absolute; bottom: 5px; left: 113px;"
    @click="back()"
  ></div>
  <div
    style="position: absolute; bottom: 13px; left: 124px; font-size: 25px; cursor: pointer;"
    @click="back()"
  ><b>-5</b></div>
  <div
    style="width: 50px; height: 50px; border-radius:50%; background: rgb(255,255,255,0.5); position: absolute; bottom: 5px; left: 167px;"
    @click="proceed()"
  ></div>
  <div
    style="position: absolute; bottom: 13px; left: 168px; font-size: 25px; cursor: pointer;"
    @click="proceed()"
  ><b>+10</b></div>
  <div
    style="position: absolute; bottom: 5px; right: 20px; font-size: 25px; color: rgb(255,255,255,0.5)"
  >{{currentTime}}/{{allTime}}秒</div>
  <img src="/images/icon/back.png" @click="toMenu()" style="width: 45px; height: 45px; position: absolute; bottom: 8px; left: 8px; cursor: pointer">
  <img src="/images/icon/reload.png" @click="reload()" style="width: 45px; height: 45px; position: absolute; bottom: 8px; left: 62px; cursor: pointer">
</template>

