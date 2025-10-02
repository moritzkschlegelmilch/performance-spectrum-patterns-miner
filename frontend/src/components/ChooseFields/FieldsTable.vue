<template>
  <div class="w-full overflow-auto">
    <div class="flex">
      <div v-for="column in columns" class="relative">
        <div :class="{'chosen': exclude.includes(column)}" class="button-overlay flex justify-center z-50">
          <Button :disabled="exclude.includes(column)" class="mt-[80px] z-50" @click="emit('choose-col', column)">
            {{ exclude.includes(column) ? 'Chosen' : 'Choose' }}
          </Button>
        </div>
        <!-- multiple tables for button display -->
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[300px]">
                {{ column }}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="row in data">
              <TableCell class="font-medium">
                <div class="min-w-[200px] text-gray-300 min-h-5 overflow-hidden">{{ row[column] ?? '' }}</div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <!-- end of table -->
      </div>
    </div>
  </div>
</template>


<script lang="js" setup>
import {computed} from "vue";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow,} from '../ui/table'
import Button from "../ui/button/Button.vue";

const props = defineProps({
    data: {
        type: Array,
        required: true
    },
    exclude: {
        type: Array,
        default: () => {
        }
    }
})

const emit = defineEmits(['choose-col'])

const columns = computed(() => {
    return Object.keys(props.data[0] ?? [])
})
</script>

<style lang="scss" scoped>
.button-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.1);

    &.chosen {
        background-color: rgba(255, 255, 255, 0.2);
    }
}
</style>