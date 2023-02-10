<script setup lang="ts">

  import { ref, onMounted } from 'vue'

  // 型情報
  type InfoPlay = {
    fileName: string;
    date: string;
  }[]

  // DOM読み込み後に実行
  onMounted(() => {
    const ele = document.documentElement;
    ele.requestFullscreen();
  })

  // App.vueのイベントを発火
  const emit = defineEmits(['go-to-home'])
  const goToHome = () => {
    emit('go-to-home')
  }

  // App.vueから情報を受けとり、初期値を設定
  const props = defineProps<{
    infoPlay:InfoPlay
    index: number
  }>();
  let ind = ref(props.index)
  let indList = [...Array(props.infoPlay.length)].map((_, i) => i)  // [0, 1, ... , inroPlay.length]
  let isShuffle = ref(false)
  let isPlay = ref(false)
  let timer = ref(0)
  // homeボタン
  const toMenu = () => {
    document.exitFullscreen()
    goToHome()
  }

  // 戻るボタン
  const back = () => {
    if(ind.value != 0){
      ind.value -= 1
    }
  }

  // 進むボタン
  const proceed = () => {
    if (ind.value + 1 < props.infoPlay.length){
      ind.value += 1
    } else {
      isPlay.value = false
      clearInterval(timer.value)
    }
  }

  // スライドショー切り替えボタン
  const pause_play_switch = () => {
    if(isPlay.value){
      isPlay.value = false
      clearInterval(timer.value)
    } else {
      isPlay.value = true
      timer.value = setInterval(proceed, 3000);
    }
  }

  // 順番切り替えボタン
  const shuffle_switch = () => {
    if(isShuffle.value){
      ind.value = indList[ind.value]
      indList = [...Array(props.infoPlay.length)].map((_, i) => i)  // [0, 1, ... , inroPlay.length]
      isShuffle.value = false
    } else {
      ind.value = 0
      indList = shuffleArray(indList)
      isShuffle.value = true
    }
  }


  const shuffleArray = (array: number[]) => {
    const cloneArray = [...array]
    for (let i = cloneArray.length - 1; i >= 0; i--) {
      let rand = Math.floor(Math.random() * (i + 1))
      let tmpStorage = cloneArray[i]
      cloneArray[i] = cloneArray[rand]
      cloneArray[rand] = tmpStorage
    }
    return cloneArray
  }
</script>

<template>
  <div class = "content" style="height: 100vh; width:100vw;">
    <img class="img" :src="infoPlay[indList[ind]].fileName" style="height: 100%; width:100%; object-fit: contain ;z-index:-100; background: black">
    <div class="circle" style="left: 5px;"  @click="toMenu()"></div>
    <img src="/images/icon/home.png" class="icon1" style="left: 8px; bottom: 8px;" @click="toMenu()">
    <div v-if="infoPlay.length > 1">
      <div class="circle" style="left: 59px;" @click="back()"></div>
      <div class="circle" style="left: 113px;" @click="proceed()"></div>
      <div class="circle" style="left: 167px;" @click="pause_play_switch()"></div>
      <div class="circle" style="left: 221px;" @click="shuffle_switch()"></div>
      <img src="/images/icon/leftarrow.png" class="icon1" style="left: 62px; bottom: 8px;" @click="back()">
      <img src="/images/icon/rightarrow.png" class="icon1" style="left: 114px; bottom: 8px;" @click="proceed()">
      <img v-if="isPlay" src="/images/icon/play.png" class="icon1" style="left: 170px; bottom: 7px;" @click="pause_play_switch()">
      <img v-if="!isPlay" src="/images/icon/pause.png" class="icon1" style="left: 170px; bottom: 7px;" @click="pause_play_switch()">
      <img v-if="!isShuffle" src="/images/icon/repeat.png" class="icon1" style="left: 223px; bottom: 8px;" @click="shuffle_switch()">
      <img v-if="isShuffle" src="/images/icon/shuffle.png" class="icon2" style="left: 226px; bottom: 11px;" @click="shuffle_switch()">
    </div>
    <div style="position: absolute; bottom: 5px; right: 20px; font-size: 25px; color: rgb(255,255,255,0.5)">
      <span> {{ infoPlay[indList[ind]].date }}</span>
    </div>
  </div>
</template>

<style scoped>
.content {
  overflow-x:hidden;
  overflow-y:hidden;
}
.circle{
  width: 50px;
  height: 50px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  bottom: 5px;
  cursor: pointer;
}
.icon1{
  width: 45px;
  height: 45px;
  position: absolute;
  cursor: pointer;
}
.icon2{
  width: 38px;
  height: 38px;
  position: absolute;
  cursor: pointer;
}
</style>

