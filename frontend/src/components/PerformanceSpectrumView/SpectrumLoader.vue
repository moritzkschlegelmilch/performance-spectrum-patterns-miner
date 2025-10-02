<template>
  <div class="h-[200px] w-full flex items-center justify-center relative overflow-hidden">
    <Skeleton class="h-full w-full absolute"></Skeleton>
    <Loader2 class="animate-spin" :size="32"></Loader2>
  </div>
</template>

<script setup lang="js">

import {Skeleton} from "@/components/ui/skeleton";
import {Loader2} from 'lucide-vue-next';
</script>

<style scoped lang="scss">

</style>