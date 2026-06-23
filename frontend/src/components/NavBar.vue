<template>
  <nav class="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm shadow-sm z-50">
    <div class="bg-gray-50 py-2 border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center text-sm text-gray-600">
        <span>欢迎访问昆明学院智慧农业1班项目网站！</span>
        <div class="flex items-center space-x-4">
          <span>联系我们</span>
          <span>|</span>
          <span>加入收藏</span>
        </div>
      </div>
    </div>
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-green-600 rounded-lg flex items-center justify-center">
            <GraduationCap class="w-10 h-10 text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-800">昆明学院</h1>
            <p class="text-sm text-gray-600">智慧农业1班 · 图像检测系统</p>
          </div>
        </div>
        
        <div class="hidden md:flex items-center space-x-2">
          <input 
            type="text" 
            placeholder="请输入搜索内容..." 
            class="px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:border-green-500"
          />
          <button class="px-4 py-2 bg-green-600 text-white rounded-r-lg hover:bg-green-700 transition-colors">
            搜索
          </button>
        </div>
      </div>
    </div>
    
    <div class="bg-green-600">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center space-x-1">
          <button 
            v-for="item in navItems" 
            :key="item.id"
            @click="$emit('navigate', item.id)"
            :class="[
              'px-6 py-3 text-white font-medium transition-colors duration-200 hover:bg-green-700',
              currentPage === item.id ? 'bg-green-700' : ''
            ]"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="mobileMenuOpen" class="md:hidden bg-green-600">
      <div class="px-4 py-4 space-y-2">
        <button 
          v-for="item in navItems" 
          :key="item.id"
          @click="handleMobileNav(item.id)"
          :class="[
            'block w-full text-left px-4 py-2 rounded-lg text-white font-medium transition-colors',
            currentPage === item.id ? 'bg-green-700' : 'hover:bg-green-700'
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
import { GraduationCap } from 'lucide-vue-next'

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
