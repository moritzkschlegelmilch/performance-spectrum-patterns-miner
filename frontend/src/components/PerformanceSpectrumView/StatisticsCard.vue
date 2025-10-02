<template>
  <Card class="w-full p-3 min-w-0">
    <CardContent class="p-3 flex flex-col justify-center h-full">
      <div class="text-gray-500 text-sm">{{title}}</div>
      <div class="text-xl font-bold">
        <slot></slot>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="js">

import CardContent from "@/components/ui/card/CardContent.vue";
import Card from "@/components/ui/card/Card.vue";


defineProps({
    title: {
        type: String,
        required: true
    },
})
</script>

<style scoped lang="scss">

</style>