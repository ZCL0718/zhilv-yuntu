<script setup lang="ts">
import { message } from "ant-design-vue";
import { onMounted, ref, watch } from "vue";

import { getTokenStats } from "../services/api";
import type { TokenStatsResponse, TokenUsage } from "../types";

const props = defineProps<{ active: boolean }>();
const loading = ref(false);
const stats = ref<TokenStatsResponse | null>(null);

function formatNumber(value: number): string {
  return value.toLocaleString("zh-CN");
}

function promptTokens(usage: TokenUsage): number {
  return usage.rewrite_prompt_tokens + usage.embedding_prompt_tokens
    + usage.planner_prompt_tokens + usage.rerank_prompt_tokens;
}

function completionTokens(usage: TokenUsage): number {
  return usage.rewrite_completion_tokens + usage.embedding_completion_tokens
    + usage.planner_completion_tokens + usage.rerank_completion_tokens;
}

function totalTokens(usage: TokenUsage): number {
  return promptTokens(usage) + completionTokens(usage);
}

async function loadStats() {
  loading.value = true;
  try {
    stats.value = await getTokenStats();
  } catch (error) {
    console.error(error);
    message.error("Token 统计加载失败，请确认后端服务已启动。");
  } finally {
    loading.value = false;
  }
}

onMounted(() => { if (props.active) void loadStats(); });
watch(() => props.active, (active) => { if (active) void loadStats(); });
</script>

<template>
  <section class="stats-page">
    <div class="ios-card stats-header">
      <div>
        <h2 class="stats-title">Token 统计</h2>
        <p class="stats-desc">查看已保存行程中各个 AI 阶段的调用消耗</p>
      </div>
      <button class="stats-button" :disabled="loading" @click="loadStats">
        {{ loading ? "加载中..." : "刷新" }}
      </button>
    </div>

    <div v-if="loading && !stats" class="ios-card stats-empty">正在加载统计...</div>
    <div v-else-if="!stats || stats.trip_count === 0" class="ios-card stats-empty">
      还没有 Token 统计数据。请先生成并保存一条行程。
    </div>

    <template v-else>
      <div class="summary-grid">
        <div class="ios-card summary-card"><span>总 Token</span><strong>{{ formatNumber(stats.total_tokens) }}</strong><small>所有已保存行程</small></div>
        <div class="ios-card summary-card"><span>输入 Token</span><strong>{{ formatNumber(stats.total_prompt_tokens) }}</strong><small>Prompt 与检索输入</small></div>
        <div class="ios-card summary-card"><span>输出 Token</span><strong>{{ formatNumber(stats.total_completion_tokens) }}</strong><small>模型生成输出</small></div>
        <div class="ios-card summary-card"><span>统计行程</span><strong>{{ formatNumber(stats.trip_count) }}</strong><small>已保存记录</small></div>
      </div>

      <div class="ios-card table-card">
        <h3>按行程查看</h3>
        <p class="stats-desc">统计后端实际记录到的 Token 使用量。</p>
        <div class="table-scroll">
          <table>
            <thead><tr><th>目的地</th><th>总 Token</th><th>输入</th><th>输出</th><th>Rewrite</th><th>Embedding</th><th>Rerank</th><th>Planner</th></tr></thead>
            <tbody>
              <tr v-for="item in stats.items" :key="item.trip_id">
                <td><strong>{{ item.destination }}</strong><small>{{ item.trip_id }}</small></td>
                <td>{{ formatNumber(totalTokens(item.token_usage)) }}</td>
                <td>{{ formatNumber(promptTokens(item.token_usage)) }}</td>
                <td>{{ formatNumber(completionTokens(item.token_usage)) }}</td>
                <td>{{ formatNumber(item.token_usage.rewrite_prompt_tokens + item.token_usage.rewrite_completion_tokens) }}</td>
                <td>{{ formatNumber(item.token_usage.embedding_prompt_tokens + item.token_usage.embedding_completion_tokens) }}</td>
                <td>{{ formatNumber(item.token_usage.rerank_prompt_tokens + item.token_usage.rerank_completion_tokens) }}</td>
                <td>{{ formatNumber(item.token_usage.planner_prompt_tokens + item.token_usage.planner_completion_tokens) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.stats-page { display: grid; gap: 12px; }
.ios-card { padding: 20px; border-radius: 12px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.stats-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.stats-title, .table-card h3 { margin: 0 0 4px; color: #1c1c1e; }
.stats-title { font-size: 22px; }
.table-card h3 { font-size: 17px; }
.stats-desc { margin: 0; color: #8e8e93; font-size: 13px; }
.stats-empty { padding: 40px 20px; color: #8e8e93; text-align: center; }
.stats-button { border: 0; border-radius: 8px; padding: 7px 16px; color: #fff; background: #007aff; cursor: pointer; }
.stats-button:disabled { opacity: .5; cursor: not-allowed; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.summary-card { display: grid; gap: 6px; }
.summary-card span { color: #636366; font-size: 13px; }
.summary-card strong { color: #1c1c1e; font-size: 28px; }
.summary-card small { color: #8e8e93; font-size: 12px; }
.table-card { overflow: hidden; }
.table-scroll { margin-top: 16px; overflow-x: auto; }
table { width: 100%; min-width: 850px; border-collapse: collapse; color: #3c3c43; font-size: 13px; }
th, td { padding: 11px 9px; border-bottom: 1px solid #f0f0f2; text-align: right; white-space: nowrap; }
th:first-child, td:first-child { text-align: left; }
th { color: #8e8e93; font-size: 12px; font-weight: 500; }
td strong, td small { display: block; } td small { margin-top: 3px; color: #8e8e93; font-size: 11px; }
@media (max-width: 900px) { .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { .stats-header { align-items: flex-start; flex-direction: column; } .summary-card strong { font-size: 23px; } }
</style>
