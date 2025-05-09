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

  let tooltip = ref({
    "home1": false,
    "home2": false,
    "repeat1": false,
    "repeat2": false,
    "shuffle1": false,
    "shuffle2": false
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
      "home2": false,
      "repeat1": false,
      "repeat2": false,
      "shuffle1": false,
      "shuffle2": false
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
  const mover = (key: "home1" | "shuffle1" | "repeat1" | "home2" | "shuffle2" | "repeat2") => {
    tooltip.value[key] = true
  }
  const mleave = (key: "home1" | "shuffle1" | "repeat1" | "home2" | "shuffle2" | "repeat2") => {
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
      else if (event.key == " ") {
        pause_or_play()
      }
    }
  )

</script>

<template>
  <div class = "content" style="height: 100vh; width:100vw;">
    <img class="img" @click="pause_or_play()" :src="infoPlay[indList[ind]].fileName" style="height: 100%; width:100%; object-fit: contain ;z-index:-100; background: black">
    <div class="circle" style="left: 5px;" @click="toMenu()" @mouseover="mover('home1')" @mouseleave="mleave('home1')"></div>
    <img src="/images/icon/home.png" class="icon1" style="left: 10px; top: 10px;" @click="toMenu()" @mouseover="mover('home2')" @mouseleave="mleave('home2')">
    <div v-if="infoPlay.length > 1">
      <!-- <div class="circle" style="left: 49px;" @click="back()" @mouseover="mover('back1')" @mouseleave="mleave('back1')"></div>
      <div class="circle" style="left: 93px;" @click="proceed()" @mouseover="mover('proceed1')" @mouseleave="mleave('proceed1')"></div> -->
      <!-- <div v-if="!isShuffle" class="circle" style="left: 137px;" @click="shuffle_switch()" @mouseover="mover('repeat1')" @mouseleave="mleave('repeat1')"></div>
      <div v-if= "isShuffle" class="circle" style="left: 137px;" @click="shuffle_switch()" @mouseover="mover('shuffle1')" @mouseleave="mleave('shuffle1')"></div> -->
      <div v-if="!isShuffle" class="circle" style="left: 49px;" @click="shuffle_switch()"></div>
      <div v-if= "isShuffle" class="circle" style="left: 49px;" @click="shuffle_switch()"></div>
      
      <!-- <img src="/images/icon/leftarrow.png" class="icon1" style="left: 54px; bottom: 8px;" @click="back()" @mouseover="mover('back2')" @mouseleave="mleave('back2')">
      <img src="/images/icon/rightarrow.png" class="icon1" style="left: 98px; bottom: 8px;" @click="proceed()" @mouseover="mover('proceed2')" @mouseleave="mleave('proceed2')"> -->
      <!-- <img v-if="!isShuffle" src="/images/icon/repeat.png" class="icon1" style="left: 142px; top: 10px;" @click="shuffle_switch()" @mouseover="mover('repeat2')" @mouseleave="mleave('repeat2')">
      <img v-if="isShuffle" src="/images/icon/shuffle.png" class="icon2" style="left: 143px; top: 11px;" @click="shuffle_switch()" @mouseover="mover('shuffle2')" @mouseleave="mleave('shuffle2')"> -->
      <img v-if="!isShuffle" src="/images/icon/repeat.png" class="icon1" style="left: 54px; top: 10px;" @click="shuffle_switch()">
      <img v-if="isShuffle" src="/images/icon/shuffle.png" class="icon2" style="left: 55px; top: 11px;" @click="shuffle_switch()">
    </div>
    <div class="tooltip" style="left: 5px" v-if="tooltip['home1'] || tooltip['home2'] ">ホームに戻る</div>
    <!-- <div class="tooltip" style="left: 49px" v-if="tooltip['back1'] || tooltip['back2']">前へ戻る</div>
    <div class="tooltip" style="left: 93px" v-if="tooltip['proceed1'] || tooltip['proceed2']">次へ進む</div> -->
    <div class="tooltip" style="left: 142px" v-if="tooltip['shuffle1'] || tooltip['shuffle2']">シャッフル無しに切り替え</div>
    <div class="tooltip" style="left: 142px" v-if="tooltip['repeat1'] || tooltip['repeat2']">シャッフル有りに切り替え </div>
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
  width: 40px;
  height: 40px;
  border-radius:50%;
  background: rgb(255,255,255,0.5);
  position: absolute;
  top: 5px;
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
  top: 50px;
  padding: 2px;
  position: absolute;
  border: solid 0.5px #3a2411;
  background: #f1eac3;
}</style>

