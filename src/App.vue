<script setup lang="ts">
  import { ref, reactive, computed } from 'vue'
  import Home from './components/Home.vue'
  import Play from './components/Play.vue'

  // 動的コンポーネントの制御
  let inHome = ref(true)
  const activeComponent = computed(() => {
    if (inHome.value){
      return Home
    } else {
      return Play
    }
  })

  // 画面遷移時の情報の受け渡し
  type Info = {
    time1?: number;
    time2?: number;
    fileName?: string;
  }
  let info:Info = reactive({ })
  const changePage = (obj:Info) => {
    if (inHome.value) {  // home画面からplay画面へ遷移
      info = obj
      inHome.value = false
    } else {  // play画面からhome画面へ遷移
      inHome.value = true
    }
  }

</script>

<template>
  <KeepAlive include="Home">
    <component :is="activeComponent" :info_p="info" @change-page="changePage"></component>
  </KeepAlive>
</template>
