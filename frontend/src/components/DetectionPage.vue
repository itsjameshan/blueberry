<template>
  <div class="min-h-screen bg-gray-50">
    <section class="bg-gradient-to-br from-green-600 via-emerald-600 to-teal-600 text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold mb-4">检测功能</h1>
          <p class="text-lg text-green-100">选择检测方式，开始您的图像检测之旅</p>
        </div>
      </div>
    </section>

    <section class="py-12 bg-white border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap justify-center gap-4">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 rounded-lg font-medium transition-all duration-300',
              activeTab === tab.id 
                ? 'bg-primary-600 text-white shadow-lg' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            <component :is="tab.icon" class="w-5 h-5 inline-block mr-2" />
            {{ tab.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div v-if="activeTab === 'single'" class="max-w-2xl mx-auto">
          <div class="card">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">单图检测</h3>
            <div 
              @click="triggerFileInput('single')"
              @dragover.prevent="dragOver = true"
              @dragleave="dragOver = false"
              @drop.prevent="handleDrop('single', $event)"
              :class="[
                'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300',
                dragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              ]"
            >
              <ImageIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p class="text-gray-600 mb-2">点击或拖拽图片到此处</p>
              <p class="text-sm text-gray-400">支持 JPG、PNG、BMP 格式，最大 10MB</p>
              <input type="file" id="single-file" class="hidden" accept="image/*" @change="handleFileSelect('single', $event)" />
            </div>
            
            <div v-if="singleImage" class="mt-6">
              <h4 class="font-medium text-gray-800 mb-3">已选择的图片</h4>
              <img :src="singleImage" class="max-w-full h-64 object-contain rounded-lg border" />
              <button @click="startSingleDetection" class="btn-primary mt-4 w-full">
                <Loader2 v-if="singleDetecting" class="w-5 h-5 inline-block mr-2 animate-spin" />
                {{ singleDetecting ? '检测中...' : '开始检测' }}
              </button>
            </div>

            <div v-if="singleResult" class="mt-6 p-4 bg-green-50 rounded-lg">
              <h4 class="font-medium text-green-800 mb-2">检测结果</h4>
              <div class="space-y-2">
                <p><span class="text-gray-600">检测类型：</span>{{ singleResult.type }}</p>
                <p><span class="text-gray-600">置信度：</span>{{ singleResult.confidence }}</p>
                <p><span class="text-gray-600">检测时间：</span>{{ singleResult.time }}</p>
                <p><span class="text-gray-600">结果：</span>{{ singleResult.result }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'batch'" class="max-w-4xl mx-auto">
          <div class="card">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">批量检测</h3>
            <div 
              @click="triggerFileInput('batch')"
              @dragover.prevent="batchDragOver = true"
              @dragleave="batchDragOver = false"
              @drop.prevent="handleBatchDrop($event)"
              :class="[
                'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300',
                batchDragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              ]"
            >
              <ImagesIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p class="text-gray-600 mb-2">点击或拖拽多张图片到此处</p>
              <p class="text-sm text-gray-400">支持同时上传最多 10 张图片</p>
              <input type="file" id="batch-file" class="hidden" accept="image/*" multiple @change="handleBatchFileSelect($event)" />
            </div>
            
            <div v-if="batchImages.length > 0" class="mt-6">
              <h4 class="font-medium text-gray-800 mb-3">已选择 {{ batchImages.length }} 张图片</h4>
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div v-for="(img, index) in batchImages" :key="index" class="relative group">
                  <img :src="img" class="w-full h-24 object-cover rounded-lg border" />
                  <button @click="removeBatchImage(index)" class="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <X class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <button @click="startBatchDetection" class="btn-primary mt-4">
                <Loader2 v-if="batchDetecting" class="w-5 h-5 inline-block mr-2 animate-spin" />
                {{ batchDetecting ? '检测中...' : '开始批量检测' }}
              </button>
            </div>

            <div v-if="batchResults.length > 0" class="mt-6">
              <h4 class="font-medium text-gray-800 mb-3">检测结果</h4>
              <div class="space-y-3">
                <div v-for="(result, index) in batchResults" :key="index" class="p-4 bg-gray-50 rounded-lg">
                  <div class="flex items-center gap-4">
                    <img :src="result.image" class="w-16 h-16 object-cover rounded-lg" />
                    <div class="flex-1">
                      <p class="font-medium text-gray-800">图片 {{ index + 1 }}</p>
                      <p class="text-sm text-gray-600">类型：{{ result.type }} | 置信度：{{ result.confidence }}</p>
                    </div>
                    <span :class="[
                      'px-3 py-1 rounded-full text-sm font-medium',
                      result.pass ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    ]">
                      {{ result.pass ? '通过' : '未通过' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'history'" class="max-w-4xl mx-auto">
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-800">检测记录</h3>
              <select v-model="filterType" class="px-4 py-2 border rounded-lg text-gray-600">
                <option value="all">全部类型</option>
                <option value="single">单图检测</option>
                <option value="batch">批量检测</option>
                <option value="large">大图检测</option>
              </select>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b">
                    <th class="text-left py-3 px-4 font-semibold text-gray-700">检测时间</th>
                    <th class="text-left py-3 px-4 font-semibold text-gray-700">类型</th>
                    <th class="text-left py-3 px-4 font-semibold text-gray-700">数量</th>
                    <th class="text-left py-3 px-4 font-semibold text-gray-700">结果</th>
                    <th class="text-left py-3 px-4 font-semibold text-gray-700">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in filteredRecords" :key="record.id" class="border-b hover:bg-gray-50">
                    <td class="py-3 px-4 text-gray-600">{{ record.time }}</td>
                    <td class="py-3 px-4">
                      <span :class="[
                        'px-2 py-1 rounded text-xs font-medium',
                        record.type === 'single' ? 'bg-blue-100 text-blue-700' :
                        record.type === 'batch' ? 'bg-purple-100 text-purple-700' :
                        'bg-orange-100 text-orange-700'
                      ]">
                        {{ record.typeLabel }}
                      </span>
                    </td>
                    <td class="py-3 px-4 text-gray-600">{{ record.count }} 张</td>
                    <td class="py-3 px-4">
                      <span :class="[
                        'px-2 py-1 rounded text-xs font-medium',
                        record.pass ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      ]">
                        {{ record.pass ? '通过' : '未通过' }}
                      </span>
                    </td>
                    <td class="py-3 px-4">
                      <button @click="viewRecord(record)" class="text-primary-600 hover:text-primary-700 font-medium">
                        <Eye class="w-5 h-5 inline-block" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex justify-center mt-6">
              <button class="btn-secondary">加载更多</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'large'" class="max-w-2xl mx-auto">
          <div class="card">
            <h3 class="text-xl font-semibold text-gray-800 mb-6">大图检测</h3>
            <p class="text-gray-600 mb-6">
              大图检测功能专为处理大尺寸图像设计，采用分片处理技术，确保检测效率和准确性。
            </p>
            <div 
              @click="triggerFileInput('large')"
              @dragover.prevent="largeDragOver = true"
              @dragleave="largeDragOver = false"
              @drop.prevent="handleDrop('large', $event)"
              :class="[
                'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300',
                largeDragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              ]"
            >
              <FileImageIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p class="text-gray-600 mb-2">点击或拖拽大图到此处</p>
              <p class="text-sm text-gray-400">支持超大尺寸图片，自动分片处理</p>
              <input type="file" id="large-file" class="hidden" accept="image/*" @change="handleFileSelect('large', $event)" />
            </div>
            
            <div v-if="largeImage" class="mt-6">
              <h4 class="font-medium text-gray-800 mb-3">已选择的图片</h4>
              <div class="bg-gray-100 rounded-lg p-4">
                <p class="text-gray-600">图片信息：{{ largeImageInfo }}</p>
              </div>
              <button @click="startLargeDetection" class="btn-primary mt-4 w-full">
                <Loader2 v-if="largeDetecting" class="w-5 h-5 inline-block mr-2 animate-spin" />
                {{ largeDetecting ? '分片检测中... ' + largeProgress + '%' : '开始大图检测' }}
              </button>
            </div>

            <div v-if="largeResult" class="mt-6 p-4 bg-green-50 rounded-lg">
              <h4 class="font-medium text-green-800 mb-2">大图检测结果</h4>
              <div class="space-y-2">
                <p><span class="text-gray-600">分片数量：</span>{{ largeResult.tiles }}</p>
                <p><span class="text-gray-600">检测类型：</span>{{ largeResult.type }}</p>
                <p><span class="text-gray-600">置信度：</span>{{ largeResult.confidence }}</p>
                <p><span class="text-gray-600">检测时间：</span>{{ largeResult.time }}</p>
                <p><span class="text-gray-600">结果：</span>{{ largeResult.result }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="bg-gray-800 text-white py-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-gray-400">© 2024 智能图像检测平台. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Image as ImageIcon, Images as ImagesIcon, FileImage as FileImageIcon, History, Eye, X, Loader2 } from 'lucide-vue-next'

const activeTab = ref('single')
const dragOver = ref(false)
const batchDragOver = ref(false)
const largeDragOver = ref(false)

const singleImage = ref(null)
const singleDetecting = ref(false)
const singleResult = ref(null)

const batchImages = ref([])
const batchDetecting = ref(false)
const batchResults = ref([])

const filterType = ref('all')
const records = ref([
  { id: 1, time: '2024-01-15 14:30:25', type: 'single', typeLabel: '单图检测', count: 1, pass: true },
  { id: 2, time: '2024-01-15 13:20:18', type: 'batch', typeLabel: '批量检测', count: 5, pass: true },
  { id: 3, time: '2024-01-14 16:45:32', type: 'large', typeLabel: '大图检测', count: 1, pass: false },
  { id: 4, time: '2024-01-14 10:15:47', type: 'single', typeLabel: '单图检测', count: 1, pass: true },
  { id: 5, time: '2024-01-13 09:30:12', type: 'batch', typeLabel: '批量检测', count: 8, pass: true }
])

const largeImage = ref(null)
const largeImageInfo = ref('')
const largeDetecting = ref(false)
const largeProgress = ref(0)
const largeResult = ref(null)

const tabs = [
  { id: 'single', label: '单图检测', icon: ImageIcon },
  { id: 'batch', label: '批量检测', icon: ImagesIcon },
  { id: 'history', label: '检测记录', icon: History },
  { id: 'large', label: '大图检测', icon: FileImageIcon }
]

const filteredRecords = computed(() => {
  if (filterType.value === 'all') return records.value
  return records.value.filter(r => r.type === filterType.value)
})

const triggerFileInput = (type) => {
  document.getElementById(`${type}-file`).click()
}

const handleFileSelect = (type, event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      if (type === 'single') {
        singleImage.value = e.target.result
        singleResult.value = null
      } else if (type === 'large') {
        largeImage.value = e.target.result
        largeImageInfo.value = `${file.name} - ${(file.size / 1024 / 1024).toFixed(2)} MB`
        largeResult.value = null
      }
    }
    reader.readAsDataURL(file)
  }
}

const handleDrop = (type, event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    dragOver.value = false
    largeDragOver.value = false
    const reader = new FileReader()
    reader.onload = (e) => {
      if (type === 'single') {
        singleImage.value = e.target.result
        singleResult.value = null
      } else if (type === 'large') {
        largeImage.value = e.target.result
        largeImageInfo.value = `${file.name} - ${(file.size / 1024 / 1024).toFixed(2)} MB`
        largeResult.value = null
      }
    }
    reader.readAsDataURL(file)
  }
}

const handleBatchFileSelect = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.type.startsWith('image/') && batchImages.value.length < 10) {
      const reader = new FileReader()
      reader.onload = (e) => {
        batchImages.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
  batchResults.value = []
}

const handleBatchDrop = (event) => {
  batchDragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  files.forEach(file => {
    if (file.type.startsWith('image/') && batchImages.value.length < 10) {
      const reader = new FileReader()
      reader.onload = (e) => {
        batchImages.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
  batchResults.value = []
}

const removeBatchImage = (index) => {
  batchImages.value.splice(index, 1)
}

const startSingleDetection = async () => {
  singleDetecting.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  singleResult.value = {
    type: '正常图像',
    confidence: '99.2%',
    time: '2024-01-15 15:30:25',
    result: '检测通过，图像质量良好'
  }
  singleDetecting.value = false
}

const startBatchDetection = async () => {
  batchDetecting.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))
  batchResults.value = batchImages.value.map((img, index) => ({
    image: img,
    type: index % 3 === 0 ? '异常图像' : '正常图像',
    confidence: (95 + Math.random() * 5).toFixed(1) + '%',
    pass: index % 5 !== 0
  }))
  batchDetecting.value = false
}

const startLargeDetection = async () => {
  largeDetecting.value = true
  largeProgress.value = 0
  for (let i = 0; i <= 100; i += 10) {
    largeProgress.value = i
    await new Promise(resolve => setTimeout(resolve, 300))
  }
  largeResult.value = {
    tiles: 16,
    type: '高分辨率图像',
    confidence: '98.7%',
    time: '2024-01-15 15:35:42',
    result: '检测通过，图像细节清晰'
  }
  largeDetecting.value = false
}

const viewRecord = (record) => {
  alert(`查看记录: ${record.time}`)
}
</script>
