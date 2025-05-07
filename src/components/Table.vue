<script setup lang="ts">

  type InfoGant = {
    "name": string;
    "gant": {[key in string]: number[]}
  }[]

  // Nav.vueから受け取る情報
  const props = defineProps<{
    infoGant: InfoGant
    yearList: number[]
    monthList: number[][]
    selectedYYYYMM: number
    cellWidth: number
    allWidth: number
  }>();

  // 定数
  const cellWidth = props.cellWidth
  const cellWidthPx = String(cellWidth) + "px"
  const allWidth = props.allWidth
  const allWidthPx = String(allWidth) + "px"
  const spaceBetweenCell = 4
  const spaceBetweenGant = 14
  const spaceBetweenLineLegend = 2

  // css（線をどう引くか）
  const retGantPosition = (x1:number, x2:number, num:number, line:boolean) => {
    // x1, x2: infoGantのvalue[0], [1]
    if (x2 === -1){
      x2 = 0
      for(const ml of props.monthList){
        x2 += ml.length
      }
    }
    const width = String((x2 - x1) * cellWidth - spaceBetweenCell) + 'px'
    const marginLeft = String(x1 * cellWidth + allWidth) + 'px'
    let marginTop = "0px"
    if (line){
      marginTop = String(num * spaceBetweenGant) + 'px'
    } else {
      marginTop = String(num * spaceBetweenGant + spaceBetweenLineLegend) + 'px'
    }
    return {'width': width, 'margin-left': marginLeft, 'marginTop': marginTop}
  }

  // Nav.vueで定義されるイベントを発火
  const emit = defineEmits(['change-yyyymm'])
  const updateYYYYMM = (yyyymm: number) => {
    emit('change-yyyymm', yyyymm)
  }

</script>

<template>
  <table >
    <!-- セル幅調整 -->
    <colgroup>
      <col :style="{width: allWidthPx}">
      <template v-for="mList in monthList">
        <template v-for="_ in mList">
          <col :style="{width: cellWidthPx}">
        </template>
      </template>
    </colgroup>

    <!-- 年 -->
    <tr align="left">
      <th></th>
      <th v-for="(year, i) in yearList" :key="String(year)" :colspan="monthList[i].length">{{ year }}</th>
    </tr>

    <!-- 月 -->
    <tr align="center">
      <td
        @click="updateYYYYMM(0)"
        :class="{selected: 0 === selectedYYYYMM}"> Playlist </td>
      <template v-for="(mList, i) in monthList">
        <td v-for="month in mList"
          :key="String(month)"
          :class="{selected: (yearList[i] * 100 + month) === selectedYYYYMM}"
          @click="updateYYYYMM(yearList[i] * 100 + month)"
        >{{ month }}</td>
      </template>
    </tr>
  </table>

  <!-- 線 -->
  <div class="gant">
    <template v-for="(info, num) in props.infoGant">
      <template v-for="(pos, age) in info.gant">
        <span class="line"
              :style="retGantPosition(pos[0], pos[1], num, true)">
        </span>
        <span class="legend"
              :style="retGantPosition(pos[0], pos[1], num, false)">{{ age }}
        </span>
      </template>
    </template>
  </div>
</template>


<style scoped>
  .selected{
    font-weight: bold;
    background-color: #3a2411;
    color: #dfcba5;
  }
  table{
    width: 0px;  /*これを設定しないといけない*/
    table-layout: fixed;
    line-height: 1.2;
  }
  table th{
    font-size: 14px;
    color: #3a2411;
  }
  table td{
    font-size: 20px;
    border-left: 1px dotted black;
    cursor: pointer;
    background-color: #dfcba5;
    color: #3a2411;
  }
  .gant{
    margin-top: 2px;
    position: relative;
  }
  .line{
    position: absolute;
    border-bottom: solid;
    border-width: 1px;
    color: #904644;
  }
  .legend{
    position: absolute;
    font-size: 12px;
    color: #904644;
  }
</style>

