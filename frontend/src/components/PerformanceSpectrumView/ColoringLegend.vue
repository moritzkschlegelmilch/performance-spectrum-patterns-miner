<template>
  <div class="w-full ml-2 flex gap-5">
    <div class="font-bold text-sm">Coloring</div>
    <div class="flex gap-2 items-center">
      <div class="dot" :style="{background: QUARTILE_COLORS.BLUE}"></div>
      <div class="text-sm text-gray-500">Smaller than 1st q.</div>
    </div>

    <div class="flex gap-2 items-center">
      <div class="dot" :style="{background: QUARTILE_COLORS.YELLOW}"></div>
      <div class="text-sm text-gray-500 flex items-center gap-1">
        1st <MoveHorizontal :size="18"/> 2nd quartile
      </div>
    </div>

    <div class="flex gap-2 items-center">
      <div class="dot" :style="{background: QUARTILE_COLORS.ORANGE}"></div>
      <div class="text-sm text-gray-500 flex items-center gap-1">
        2nd <MoveHorizontal :size="18"/> 3rd quartile
      </div>
    </div>

    <div class="flex gap-2 items-center">
      <div class="dot" :style="{background: QUARTILE_COLORS.RED}"></div>
      <div class="text-sm text-gray-500">Greater than 3rd q.</div>
    </div>
  </div>
</template>

<script setup lang="js">

import {QUARTILE_COLORS} from "@/constants.js";
import {MoveHorizontal} from "lucide-vue-next";
</script>

<style scoped lang="scss">

</style>