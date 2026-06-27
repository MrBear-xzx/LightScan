<template>
  <div class="sidebar">
    <div class="logo">Light<span>Scan</span></div>
    <div class="nav-item" :class="{ active: $route.path === '/dashboard' }" @click="$router.push('/dashboard')">
      仪表盘
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/scans') }" @click="$router.push('/scans')">
      扫描任务
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/vulns') }" @click="$router.push('/vulns')">
      漏洞管理
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/reports') }" @click="$router.push('/reports')">
      报表中心
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/notifications') }" @click="$router.push('/notifications')">
      通知管理
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/plugins') }" @click="$router.push('/plugins')">
      插件管理
    </div>
    <div class="nav-item" :class="{ active: $route.path.startsWith('/admin') }" @click="$router.push('/admin')">
      系统管理
    </div>
  </div>
</template>
