<template>
  <header class="w-full p-5 dark">
    <div class="max-w-7xl px-6 mx-auto flex gap-3 relative items-center">

      <img src="../../../public/images/logo_light.png" alt="Logo" class="w-10 h-10 rounded-full" />
      <div class="font-bold">Performance Spectrum Miner</div>

      <!-- links shall be centered -->
      <div class="flex gap-10 overlay">
        <RouterLink active-class="font-bold" class="text-gray-300 text-sm w-[50px]" to="/">
          Home
        </RouterLink>

        <RouterLink active-class="font-bold" class="text-gray-300 text-sm w-[80px]" to="/event-logs">
          Event logs
        </RouterLink>

        <RouterLink active-class="font-bold" class="text-gray-300 text-sm w-[50px]" to="/upload">
          Upload
        </RouterLink>
      </div>
      <!-- End of center links -->

      <a class="ml-auto" href="https://git.rwth-aachen.de/jasper.saathoff/spp-performance-spectrum-patterns-miner" target="_blank" rel="noopener noreferrer" title="Gitlab repository">
      <Gitlab :size="20" />
      </a>

    </div>
  </header>
</template>

<script lang="ts" setup>
import {Gitlab} from 'lucide-vue-next';
</script>

<style lang="scss" scoped>
.overlay {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
}
</style>