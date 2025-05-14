<script setup lang="ts">

  const props = defineProps<{
    thumbnail: {[key in string]: {"fileName": string, "id": number, "date": string, "aspectRatio": number}[]}
  }>();
  console.log(props.thumbnail)

  // Home.vueで定義されるイベントを発火
  const emit = defineEmits(['select-tag'])
  const selectTag = (tag: string) => { // 何番目のサムネイルが選択されたか
    emit('select-tag', tag)
  }

  
  let ind : {[key in string]: number}
  ind = {}
  for (let key in props.thumbnail){
    ind[key] = Math.floor(Math.random() * props.thumbnail[key].length)
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
  <template v-for="(value, tag, index) in thumbnail" :key="value[ind[tag]].id"> 
    <h2 class="index">{{ tag }}</h2>
      <div :style="retStyle(value[ind[tag]]['aspectRatio'], 16 / 9)">
          <img :src="value[ind[tag]]['fileName']" class="item" @click="selectTag(tag)">
      </div>
  </template>

</template>

<style scoped>
  .index {
    font-size: 25px;
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
  .movieTitle{
    font-size: 20px;
    margin-left: 5px;
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