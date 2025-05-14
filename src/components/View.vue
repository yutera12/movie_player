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
  let indList = [...Array(props.infoPlay.length)].map((_, i) => i)  // [0, 1, ... , infoPlay.length]
  let isShuffle = ref(false)
  let timer = ref(0)
  let pause = ref(false)
  let info = ref(true)

  let tooltip = ref({
    "home1": false,
    "home2": false
  })


  // homeボタン
  const toMenu = () => {
    document.exitFullscreen()
    goToHome()
  }

  // 戻るボタン
  const back = () => {
    if (pause.value) {
      resetTimer()
    }
    if(ind.value != 0){
      ind.value -= 1
    }
  }

  // 進むボタン
  const proceed = () => {
    if (!pause.value) {
      resetTimer()
    }
    if (ind.value + 1 < props.infoPlay.length){
      ind.value += 1
    }
  } 

  const resetTimer = () => {
    clearInterval(timer.value)
    timer.value = setInterval(proceed, 3000);
  }

  onMounted(() => {
    resetTimer()
  })

  // 順番切り替えボタン
  const shuffle_switch = () => {
    tooltip.value = {
      "home1": false,
      "home2": false
    }
    if(isShuffle.value){
      ind.value = indList[ind.value]
      indList = [...Array(props.infoPlay.length)].map((_, i) => i)  // [0, 1, ... , infoPlay.length]
      isShuffle.value = false
    } else {
      indList = shuffleArray(indList)
      ind.value = indList.indexOf(ind.value)
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
  const mover = (key: "home1" | "home2") => {
    tooltip.value[key] = true
  }
  const mleave = (key: "home1" | "home2") => {
    tooltip.value[key] = false
  }

  const pause_or_play = () => {
    console.log(pause.value)
    if (pause.value) {  // 停止中
      clearInterval(timer.value)
      timer.value = setInterval(proceed, 3000);
      pause.value = false;
    } else {  // 再生中
      clearInterval(timer.value)
      pause.value = true;
    }
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
        toMenu()
      }
      else if (event.key == "ArrowLeft") {
        back()
      }
      else if (event.key == "ArrowRight") {
        proceed()
      }
      else if (event.key == "s") {
        shuffle_switch()
      }
      else if (event.key == "i") {
        change_info()
      }
      else if (event.key == " ") {
        pause_or_play()
      }
    }
  )

</script>

<template>
  <div class = "content" style="height: 100vh; width:100vw;">
    <img class="img" @click="pause_or_play()" :src="infoPlay[indList[ind]].fileName" style="height: 100%; width:100%; object-fit: contain ;z-index:-100; background: black">
    <template v-if="info==true">
      <div class="circle" style="top: 5px;" @click="toMenu()" @mouseover="mover('home1')" @mouseleave="mleave('home1')"></div>
      <img src="/images/icon/home.png" class="icon1" style="left: 10px; top: 10px;" @click="toMenu()" @mouseover="mover('home2')" @mouseleave="mleave('home2')">
      <div v-if="infoPlay.length > 1">
        <div v-if="!isShuffle" class="circle" style="top: 49px;" @click="shuffle_switch()"></div>
        <div v-if= "isShuffle" class="circle" style="top: 49px;" @click="shuffle_switch()"></div>
        <img v-if="!isShuffle" src="/images/icon/repeat.png" class="icon1" style="top: 54px; left: 10px;" @click="shuffle_switch()">
        <img v-if="isShuffle" src="/images/icon/shuffle.png" class="icon2" style="top: 55px; left: 11px;" @click="shuffle_switch()">
      </div>
      <div class="tooltip" style="top: 10px" v-if="tooltip['home1'] || tooltip['home2'] ">ホームに戻る</div>
    </template>
    <div style="position: absolute; bottom: 5px; right: 20px; font-size: 15px; color: rgb(255,255,255,0.5)">
      <span> {{ infoPlay[indList[ind]].date }}</span>
    </div>
    <div v-if="pause==true" style="font-size: 12px; position: absolute; top: 95px; left: 7px; color: lightgray"> <span> pause </span></div>
  </div>
</template>

<style scoped>
.content {
  overflow-x:hidden;
  overflow-y:hidden;
}
.circle{
  width: 40px;
  height: 40px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  left: 5px;
  cursor: pointer;
}
.icon1{
  width: 30px;
  height: 30px;
  position: absolute;
  cursor: pointer;
}
.icon2{
  width: 28px;
  height: 28px;
  position: absolute;
  cursor: pointer;
}
.tooltip{
  left: 50px;
  padding: 2px;
  position: absolute;
  border: solid 0.5px #3a2411;
  background: #f1eac3;
}</style>

