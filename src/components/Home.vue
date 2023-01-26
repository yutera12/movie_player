<script setup lang="ts">
  import Body from './Body.vue'
  import Nav from './Nav.vue'

  // info_p =  information from parent component
  // info_c =  information from child component

  // 親コンポーネントから空の情報を受け取る
  defineProps<{
    info_p:{}
  }>();

  // 子コンポーネントから情報を受け取り、親コンポーネントに渡す
  type Info_c = {
    time1: number;
    time2: number;
    fileName: string;
  }
  const emit = defineEmits(['change-page'])
  const changePage = (info_c: Info_c) => {
    emit('change-page', info_c)
  }
</script>

<template>
  <Nav />
  <Body @change-page="changePage"/>
</template>
