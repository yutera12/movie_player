<script setup lang="ts">

 defineProps<{
    infoThumbMovie: {
      fileName: string[];
      id: number;
      totalTime: string;
      date: string;
      aspectRatio: number;
    }[],
    infoThumbPhoto: {
      fileName: string;
      id: number;
      date: string;
      aspectRatio: number;
    }[],
    selectedYYYYMM: number
  }>();

  // Home.vueで定義されるイベントを発火
  const emit = defineEmits(['go-to-play'])
  const goToPlay = (id: number, isMovie: boolean) => { // 何番目のサムネイルが選択されたか
    emit('go-to-play', id, isMovie)
  }

  const randomSelect = (fileNames: string[]) => {
    return fileNames[Math.floor(Math.random() * fileNames.length)]
  }

  const retStyle = (aspectRatio: number, base: number) => {
    // base画像: 横 = 1とすると、縦 = 1 / base、面積 = 1 / base
    // 対象画像: 横 = xとすると、縦 = x / aspectRatio、面積 = x ** 2 / aspectRatio
    // 面積を等しくするには、x ** 2 = aspectRatio / base
    //                      x = sqrt(aspectRatio / base)
    // margin = 1 - x = 1 - sqrt(aspectRatio / base)
    //
    let margin = (1 - Math.sqrt(aspectRatio / base)) / 2 * 100
    if (margin < 0){
      margin = 0
    }
    return {'margin-left': margin + "%", 'margin-right': margin + "%"}
  }
</script>


<template>
  <div v-if="infoThumbMovie.length > 0">
    <h2 class="index">動画</h2>
    <div class="grid">
      <template v-for="(v, index) in infoThumbMovie" :key="v.id">
        <div :style="retStyle(v.aspectRatio, 16 / 9)">
          <img :src="randomSelect(v.fileName)"
                class="item" @click="goToPlay(index, true)">
          <p class="item time-date">
            <div class="time">{{ v.totalTime }}</div>
            <div class="date">{{ v.date }}</div>
          </p>
        </div>
      </template>
    </div>
  </div>
  <div v-if="infoThumbPhoto.length > 0 || selectedYYYYMM == 0">
    <h2 class="index">写真 </h2>
    <span v-if="selectedYYYYMM == 0" class="index2" @click="goToPlay(0, false)">全写真スライドショー</span>
    <div class="grid">
      <template v-for="(v, index) in infoThumbPhoto" :key="v.id">
        <div :style="retStyle(v.aspectRatio, 4 / 3)">
          <img :src="v.fileName"
                class="item" @click="goToPlay(index, false)">
          <p class="item time-date">
            <div class="date">{{ v.date }}</div>
          </p>
        </div>
      </template>
    </div>
  </div>


</template>

<style scoped>
  .index {
    font-size: 20px;
    margin-bottom: 20px;
    color: #3a2411;
    max-width: 1100px;
    margin: 20px 0px 20px 5px;
  }
  .index2 {
    font-size: 16px;
    margin-left: 40px;
    text-decoration: underline;
    cursor: pointer;
  }
  img {
    cursor: pointer;
  }
  .grid{
    display: grid;
    gap: 5px;
    margin: 5px;
    grid-template-columns: repeat(auto-fit, minmax(min(250px), 1fr));
  }
  .item{
    width: 100%;
    max-width: 500px;
  }
  .comment{
    margin: 2px 4px 2px 4px;
    font-size: 10px;
  }
  .time-date{
    display:flex;
    font-size: 14px;
    justify-content: space-between;
    margin-bottom: 5px;
  }
  .time{
    margin-left: 4px;
  }
  .date{
    margin-right: 4px;
  }
</style>