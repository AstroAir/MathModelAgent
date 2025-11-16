<template>
  <div class="min-h-screen bg-background">
    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-br from-background via-background to-muted/30">
      <!-- Background Elements -->
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div class="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
      <div class="absolute top-40 right-10 w-72 h-72 bg-primary/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      <div class="absolute -bottom-8 left-20 w-72 h-72 bg-accent/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>

      <div class="relative container mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <!-- Navigation Bar -->
        <nav class="flex items-center justify-between mb-16">
          <div class="flex items-center space-x-2">
            <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <span class="text-primary-foreground font-bold text-lg">M</span>
            </div>
            <span class="text-xl font-bold text-foreground">MathModelAgent</span>
          </div>
          <div class="hidden md:flex items-center space-x-8">
            <a href="#features" class="text-muted-foreground hover:text-primary transition-colors">功能</a>
            <a href="#about" class="text-muted-foreground hover:text-primary transition-colors">关于</a>
            <button @click="router.push('/chat')" class="btn-primary px-6 py-2 rounded-full">
              立即体验
            </button>
          </div>
        </nav>

        <!-- Hero Content -->
        <div class="text-center max-w-5xl mx-auto">
          <div class="inline-flex items-center bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-8">
            <Sparkles class="w-4 h-4 mr-2" />
            革命性数学建模助手
          </div>

          <h1 class="text-4xl sm:text-5xl lg:text-7xl font-bold text-foreground mb-8 leading-tight">
            让数学建模变得
            <span class="text-gradient">
              简单高效
            </span>
          </h1>

          <p class="text-xl sm:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
            专为数学建模设计的智能助手，将传统3天的工作缩短至1小时，自动生成获奖级别的建模论文
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <button @click="router.push('/chat')"
              class="group btn-primary px-8 py-4 text-lg flex items-center">
              <span>开始建模之旅</span>
              <ArrowRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </button>
            <button class="btn-secondary px-8 py-4 text-lg flex items-center">
              <Play class="w-5 h-5 mr-2" />
              观看演示
            </button>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div class="text-center">
              <div class="text-3xl font-bold text-primary mb-2">72x</div>
              <div class="text-muted-foreground">效率提升</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary mb-2">1小时</div>
              <div class="text-muted-foreground">完成建模</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary mb-2">获奖级</div>
              <div class="text-muted-foreground">论文质量</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-24 bg-background">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-foreground mb-4">
            强大功能，一站式解决方案
          </h2>
          <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
            从问题分析到论文生成，MathModelAgent 提供完整的数学建模工作流程
          </p>
        </div>

        <!-- Enhanced Bento Grid Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-12">
          <!-- Main Feature Card - Revolutionary Breakthrough -->
          <div class="lg:col-span-8 lg:row-span-2 group">
            <div class="card-modern h-full bg-gradient-to-br from-primary/10 to-accent/10 border-border">
              <div class="p-8 h-full flex flex-col">
                <div class="flex items-center mb-6">
                  <div class="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center mr-4">
                    <Zap class="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h2 class="text-2xl font-bold text-foreground">数学建模的革命性突破</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
                  <div class="space-y-6">
                    <div class="flex items-start" v-for="(item, idx) in mainPoints.slice(0, 2)" :key="idx">
                      <div class="flex-shrink-0 mr-4">
                        <div class="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center">
                          <component :is="item.icon" class="w-6 h-6 text-primary-foreground" />
                        </div>
                      </div>
                      <div>
                        <h3 class="text-xl font-semibold mb-2 text-foreground">{{ item.title }}</h3>
                        <p class="text-muted-foreground leading-relaxed">{{ item.desc }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="space-y-6">
                    <div class="flex items-start" v-for="(item, idx) in mainPoints.slice(2)" :key="idx">
                      <div class="flex-shrink-0 mr-4">
                        <div class="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center">
                          <component :is="item.icon" class="w-6 h-6 text-primary-foreground" />
                        </div>
                      </div>
                      <div>
                        <h3 class="text-xl font-semibold mb-2 text-foreground">{{ item.title }}</h3>
                        <p class="text-muted-foreground leading-relaxed">{{ item.desc }}</p>
                      </div>
                    </div>

                    <!-- Visual Progress Indicator -->
                    <div class="mt-8 p-6 bg-card rounded-2xl border border-border">
                      <h4 class="font-semibold text-foreground mb-4">效率对比</h4>
                      <div class="space-y-3">
                        <div>
                          <div class="flex justify-between mb-2">
                            <span class="text-sm text-muted-foreground">传统方法</span>
                            <span class="text-sm font-medium text-foreground">72小时</span>
                          </div>
                          <div class="w-full bg-muted rounded-full h-2">
                            <div class="bg-secondary h-2 rounded-full" style="width: 100%"></div>
                          </div>
                        </div>
                        <div>
                          <div class="flex justify-between mb-2">
                            <span class="text-sm text-muted-foreground">MathModelAgent</span>
                            <span class="text-sm font-medium text-primary">1小时</span>
                          </div>
                          <div class="w-full bg-muted rounded-full h-2">
                            <div class="bg-primary h-2 rounded-full animate-pulse" style="width: 1.4%"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Core Features Card -->
          <div class="lg:col-span-4 group">
            <div class="card-modern h-full bg-card">
              <div class="p-6">
                <div class="flex items-center mb-6">
                  <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3">
                    <Sparkles class="w-5 h-5 text-primary-foreground" />
                  </div>
                  <h2 class="text-xl font-bold text-foreground">核心功能</h2>
                </div>
                <div class="grid grid-cols-1 gap-4">
                  <div class="flex items-start" v-for="(item, idx) in coreFeatures.slice(0, 4)" :key="idx">
                    <component :is="item.icon" class="w-5 h-5 text-primary mr-3 mt-0.5 flex-shrink-0" />
                    <p class="text-sm text-muted-foreground leading-relaxed">{{ item.text }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Multi-Agent System Card -->
          <div class="lg:col-span-4 group">
            <div class="card-modern h-full bg-gradient-to-br from-primary/10 to-accent/10 border-border">
              <div class="p-6">
                <div class="flex items-center mb-6">
                  <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3">
                    <Cpu class="w-5 h-5 text-primary-foreground" />
                  </div>
                  <h2 class="text-xl font-bold text-foreground">多智能体系统</h2>
                </div>
                <div class="space-y-4">
                  <div class="bg-card p-4 rounded-xl border border-border" v-for="(item, idx) in agents" :key="idx">
                    <p class="font-semibold text-foreground mb-1">{{ item.role }}</p>
                    <p class="text-sm text-muted-foreground">{{ item.desc }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          <!-- Technology Support Card -->
          <div class="card-modern bg-card group">
            <div class="p-6">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3">
                  <CheckCircle class="w-5 h-5 text-primary-foreground" />
                </div>
                <h2 class="text-xl font-bold text-foreground">技术支持</h2>
              </div>
              <div class="flex flex-wrap gap-2">
                <span v-for="(item, idx) in techs" :key="idx"
                  class="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-medium border border-border hover:border-primary/50 transition-colors">
                  {{ item }}
                </span>
              </div>
            </div>
          </div>

          <!-- Future Plans Card -->
          <div class="card-modern bg-gradient-to-br from-primary/10 to-accent/10 border-border group">
            <div class="p-6">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mr-3">
                  <Calendar class="w-5 h-5 text-primary-foreground" />
                </div>
                <h2 class="text-xl font-bold text-foreground">未来规划</h2>
              </div>
              <ul class="space-y-3">
                <li class="flex items-start" v-for="(item, idx) in plans" :key="idx">
                  <div class="w-5 h-5 bg-primary/20 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                    <Check class="w-3 h-3 text-primary" />
                  </div>
                  <span class="text-sm text-muted-foreground leading-relaxed">{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Enhanced CTA Card -->
          <div class="card-modern bg-primary text-primary-foreground group">
            <div class="p-6 relative overflow-hidden">
              <!-- Background Pattern -->
              <div class="absolute inset-0 bg-grid-pattern opacity-20"></div>

              <div class="relative z-10">
                <div class="flex items-center mb-4">
                  <div class="w-10 h-10 bg-primary-foreground/20 rounded-xl flex items-center justify-center mr-3">
                    <Rocket class="w-5 h-5 text-primary-foreground" />
                  </div>
                  <h2 class="text-xl font-bold">开启建模之旅</h2>
                </div>

                <p class="text-primary-foreground/80 mb-6 leading-relaxed">
                  体验革命性的数学建模助手，让复杂的建模工作变得简单高效
                </p>

                <div class="space-y-3">
                  <button class="w-full py-3 px-6 bg-background text-foreground rounded-xl font-semibold hover:bg-background/90 transition-all duration-300 transform hover:scale-105 flex items-center justify-center group"
                    @click="router.push('/chat')">
                    <span>立即体验</span>
                    <ArrowRight class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </button>

                  <div class="flex items-center justify-center text-sm text-primary-foreground/60">
                    <Users class="w-4 h-4 mr-2" />
                    <span>已有 10,000+ 用户体验</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-24 bg-background">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-6xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              为什么选择 MathModelAgent？
            </h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              我们致力于通过人工智能技术简化数学建模过程，为学生和研究人员提供高效的解决方案
            </p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
            <!-- About Us -->
            <div class="card-modern bg-card group">
              <div class="p-8">
                <div class="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center mb-6">
                  <Heart class="w-6 h-6 text-primary-foreground" />
                </div>
                <h3 class="text-xl font-bold text-foreground mb-4">关于我们</h3>
                <p class="text-muted-foreground leading-relaxed">
                  我们致力于通过人工智能技术简化数学建模过程，为学生和研究人员提供高效的解决方案。让复杂的数学建模工作变得简单高效。
                </p>
              </div>
            </div>

            <!-- Use Cases -->
            <div class="card-modern bg-card group">
              <div class="p-8">
                <div class="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center mb-6">
                  <Target class="w-6 h-6 text-primary-foreground" />
                </div>
                <h3 class="text-xl font-bold text-foreground mb-4">适用场景</h3>
                <ul class="space-y-2 text-muted-foreground">
                  <li class="flex items-center">
                    <div class="w-2 h-2 bg-primary rounded-full mr-3"></div>
                    数学建模竞赛
                  </li>
                  <li class="flex items-center">
                    <div class="w-2 h-2 bg-primary rounded-full mr-3"></div>
                    学术研究项目
                  </li>
                  <li class="flex items-center">
                    <div class="w-2 h-2 bg-primary rounded-full mr-3"></div>
                    数据分析项目
                  </li>
                  <li class="flex items-center">
                    <div class="w-2 h-2 bg-primary rounded-full mr-3"></div>
                    科研论文写作
                  </li>
                  <li class="flex items-center">
                    <div class="w-2 h-2 bg-primary rounded-full mr-3"></div>
                    教学辅助工具
                  </li>
                </ul>
              </div>
            </div>

            <!-- Contact -->
            <div class="card-modern bg-card group">
              <div class="p-8">
                <div class="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center mb-6">
                  <MessageCircle class="w-6 h-6 text-primary-foreground" />
                </div>
                <h3 class="text-xl font-bold text-foreground mb-4">联系我们</h3>
                <p class="text-muted-foreground mb-6">
                  加入我们的社区，获取最新更新和技术支持
                </p>
                <div class="flex space-x-4">
                  <a :href="QQ_GROUP" target="_blank"
                    class="w-10 h-10 bg-muted hover:bg-accent rounded-xl flex items-center justify-center transition-colors group">
                    <svg class="w-5 h-5 text-muted-foreground group-hover:text-primary" viewBox="0 0 1024 1024">
                      <path fill="currentColor" d="M824.8 613.2c-16-51.4-34.4-94.6-62.7-165.3C766.5 262.2 689.3 112 511.5 112 331.7 112 256.2 265.2 261 447.9c-28.4 70.8-46.7 113.7-62.7 165.3-34 109.5-23 154.8-14.6 155.8 18 2.2 70.1-82.4 70.1-82.4 0 49 25.2 112.9 79.8 159-26.4 8.1-85.7 29.9-71.6 53.8 11.4 19.3 196.2 12.3 249.5 6.3 53.3 6 238.1 13 249.5-6.3 14.1-23.8-45.3-45.7-71.6-53.8 54.6-46.2 79.8-110.1 79.8-159 0 0 52.1 84.6 70.1 82.4 8.5-1.1 19.5-46.4-14.5-155.8z"/>
                    </svg>
                  </a>
                  <a :href="GITHUB_LINK" target="_blank"
                    class="w-10 h-10 bg-muted hover:bg-accent rounded-xl flex items-center justify-center transition-colors group">
                    <Github class="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                  </a>
                  <a :href="TWITTER" target="_blank"
                    class="w-10 h-10 bg-muted hover:bg-accent rounded-xl flex items-center justify-center transition-colors group">
                    <Twitter class="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-card text-card-foreground py-12 border-t border-border">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-6xl mx-auto">
          <div class="flex flex-col md:flex-row items-center justify-between">
            <div class="flex items-center space-x-2 mb-4 md:mb-0">
              <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span class="text-primary-foreground font-bold">M</span>
              </div>
              <span class="text-xl font-bold">MathModelAgent</span>
            </div>

            <div class="flex items-center space-x-6 text-sm text-muted-foreground">
              <span>© 2024 MathModelAgent. All rights reserved.</span>
              <div class="hidden md:flex items-center space-x-4">
                <a href="#" class="hover:text-foreground transition-colors">隐私政策</a>
                <a href="#" class="hover:text-foreground transition-colors">服务条款</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import {
  Clock,
  Award,
  FileText,
  Sparkles,
  Search,
  Code,
  File,
  Users,
  Layers,
  Wallet,
  Cpu,
  CheckCircle,
  BarChart2,
  Calendar,
  Check,
  Mail,
  Github,
  Twitter,
  ArrowRight,
  Play,
  Zap,
  Rocket,
  Heart,
  Target,
  MessageCircle
} from 'lucide-vue-next'

import { useRouter } from 'vue-router'
import { QQ_GROUP, GITHUB_LINK, TWITTER } from '@/utils/const'

const router = useRouter()

const mainPoints = [
  {
    icon: Clock,
    title: '3天 → 1小时',
    desc: '将传统3天的比赛时间缩短至1小时，极大提升工作效率'
  },
  {
    icon: Award,
    title: '获奖级建模论文',
    desc: '自动完成一份可以获奖级别的数学建模论文，无需人工干预'
  },
  {
    icon: FileText,
    title: '完整解决方案',
    desc: '从问题分析到论文提交，一站式解决数学建模全流程'
  }
]

const coreFeatures = [
  { icon: Search, text: '自动分析问题与数学建模' },
  { icon: Code, text: '本地代码解释器' },
  { icon: File, text: '排版完整的论文生成' },
  { icon: Users, text: '多智能体协作系统' },
  { icon: Layers, text: '多种LLM模型支持' },
  { icon: Wallet, text: '低成本Agentless架构' }
]

const agents = [
  { role: '建模手', desc: '负责数学建模与分析' },
  { role: '代码手', desc: '编写代码与反思优化' },
  { role: '论文手', desc: '生成符合规范的论文' }
]

const techs = [
  'R语言', 'MATLAB', 'LaTeX模板', '视觉模型', '文献引用', '流程图绘制', '英文支持', '美赛适配'
]

const plans = [
  '更多数学建模测试案例支持',
  '引入用户交互（选择模型，重写等）',
  '代码解释器接入云端（e2b等供应商）'
]
</script>

