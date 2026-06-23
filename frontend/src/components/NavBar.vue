<template>
  <nav class="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm shadow-sm z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <Eye class="w-6 h-6 text-white" />
          </div>
          <span class="text-xl font-bold text-gray-800">检测平台</span>
        </div>
        
        <div class="hidden md:flex items-center space-x-8">
          <button 
            v-for="item in navItems" 
            :key="item.id"
            @click="$emit('navigate', item.id)"
            :class="[
              'text-gray-600 hover:text-primary-600 font-medium transition-colors duration-200',
              currentPage === item.id ? 'text-primary-600 border-b-2 border-primary-600' : ''
            ]"
          >
            {{ item.label }}
          </button>
        </div>
        
        <div class="md:hidden">
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-gray-600 hover:text-gray-800">
            <Menu class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="mobileMenuOpen" class="md:hidden bg-white border-t">
      <div class="px-4 py-4 space-y-2">
        <button 
          v-for="item in navItems" 
          :key="item.id"
          @click="handleMobileNav(item.id)"
          :class="[
            'block w-full text-left px-4 py-2 rounded-lg text-gray-600 hover:text-primary-600 hover:bg-gray-50 font-medium transition-colors',
            currentPage === item.id ? 'text-primary-600 bg-primary-50' : ''
          ]"
        >
          {{ item.label }}
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { Eye, Menu } from 'lucide-vue-next'

defineProps({
  currentPage: {
    type: String,
    default: 'home'
  }
})

const emit = defineEmits(['navigate'])

const mobileMenuOpen = ref(false)

const navItems = [
  { id: 'home', label: '首页' },
  { id: 'technology', label: '技术开发' },
  { id: 'detection', label: '检测功能' }
]

const handleMobileNav = (pageId) => {
  emit('navigate', pageId)
  mobileMenuOpen.value = false
}
</script>
