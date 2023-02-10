<script setup lang="ts">
  import Table from './Table.vue'
  type InfoGant = {
    "name": string;
    "gant": {[key in string]: number[]}
  }[]

  // Home.vueから情報を受け取り
  const props = defineProps<{
    infoGant: InfoGant
    yearList: number[]
    monthList: number[][]
    selectedYYYYMM: number
    cellWidth: number
    allWidth: number
  }>();
  const style={"height": String(95 + 20 + 13 * props.infoGant.length) + "px"}

  // Home.vueで定義されるイベントを発火
  const emit = defineEmits(['change-yyyymm'])
  const changeYYYYMM = (yyyymm: number) => {
    emit('change-yyyymm', yyyymm)
  }

</script>


<template>
  <nav class="nav" :style="style">
    <div class="title">アルバム</div>
    <div class="table">
      <Table :infoGant="infoGant"
             :yearList="yearList"
             :monthList="monthList"
             :selectedYYYYMM="selectedYYYYMM"
             :cellWidth="cellWidth"
             :allWidth="allWidth"
             @change-yyyymm="changeYYYYMM"/>
    </div>
  </nav>
</template>

<style scoped>
  .nav{
    position: relative;
    overflow-x: auto;
    overflow-y: hidden;
    background-color: #f1e2be;
  }
  .title{
    margin-left: 30px;
    margin-top: 10px;
    font-size: 30px;
    color: #3a2411;

  }
  .table{
    margin-top: 10px
  }
</style>

