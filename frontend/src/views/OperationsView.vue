<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import RequestState from '@/components/common/RequestState.vue'
import StatCard from '@/components/common/StatCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { api } from '@/services/api'
import type { Build, Deployment, DeploymentStats, Incident, IncidentStats, Issue, Repository } from '@/types/api'

const router = useRouter()
const repositories = ref<Repository[]>([])
const repositoryCount = ref(0)
const builds = ref<Build[]>([])
const buildCount = ref(0)
const slowestBuilds = ref<Build[]>([])
const deployments = ref<Deployment[]>([])
const deploymentCount = ref(0)
const deploymentStats = ref<DeploymentStats | null>(null)
const incidents = ref<Incident[]>([])
const incidentCount = ref(0)
const incidentStats = ref<IncidentStats | null>(null)
const issues = ref<Issue[]>([])
const issueCount = ref(0)
const loading = ref(true)
const errors = reactive<Record<string, string>>({})

const displayedRepositories = computed(() => repositories.value)
const displayedBuilds = computed(() => builds.value)
const displayedDeployments = computed(() => deployments.value)
const displayedIncidents = computed(() => incidents.value)
const displayedIssues = computed(() => issues.value)

const suggestedQuestions = {
  repositories: [
    'Which repositories use Python?',
    'Which repositories use TypeScript?',
    'Which repositories are private?',
    'Which repositories belong to Platform?',
    'How many repositories are there?',
  ],
  builds: [
    'Which builds are taking the longest?',
    'Which builds failed?',
    'Which repository has the slowest build?',
    'Show me recent failed builds.',
    'What are the longest build durations?',
  ],
  deployments: [
    'How many deployments succeeded?',
    'How many deployments failed?',
    'Which service has the most deployments?',
    'Show recent failed deployments.',
    'What is the deployment success rate?',
  ],
  incidents: [
    'Which incidents are currently open?',
    'Which service has the most incidents?',
    'Show the highest severity incidents.',
    'How many incidents are open?',
    'Which incidents are resolved?',
  ],
  issues: [
    'Which issues are currently open?',
    'Which issues are assigned?',
    'Which repository has the most issues?',
    'Show issues with high priority.',
    'Show the open issues for mcpilot-api.',
  ],
}

const deploymentSuccessRate = computed(() => {
  if (!deploymentStats.value || deploymentStats.value.total_deployments === 0) return '—'
  return `${Math.round((deploymentStats.value.successful_deployments / deploymentStats.value.total_deployments) * 100)}%`
})

function recordError(name: string, reason: unknown) {
  errors[name] = reason instanceof Error ? reason.message : 'This signal is unavailable right now.'
}

async function loadOperations() {
  loading.value = true
  for (const key of Object.keys(errors)) delete errors[key]

  const results = await Promise.allSettled([
    api.repositories(),
    api.builds(),
    api.slowestBuilds(),
    api.deployments(),
    api.deploymentStats(),
    api.incidents(),
    api.incidentStats(),
    api.issues(),
  ])
  const [
    repositoryResult,
    buildResult,
    slowestBuildResult,
    deploymentResult,
    deploymentStatsResult,
    incidentResult,
    incidentStatsResult,
    issueResult,
  ] = results

  if (repositoryResult.status === 'fulfilled') {
    repositories.value = repositoryResult.value.repositories
    repositoryCount.value = repositoryResult.value.count
  } else {
    recordError('repositories', repositoryResult.reason)
  }

  if (buildResult.status === 'fulfilled') {
    builds.value = buildResult.value.builds
    buildCount.value = buildResult.value.count
  } else {
    recordError('builds', buildResult.reason)
  }

  if (slowestBuildResult.status === 'fulfilled') {
    slowestBuilds.value = slowestBuildResult.value.builds
  } else {
    recordError('slowestBuilds', slowestBuildResult.reason)
  }

  if (deploymentResult.status === 'fulfilled') {
    deployments.value = deploymentResult.value.deployments
    deploymentCount.value = deploymentResult.value.count
  } else {
    recordError('deployments', deploymentResult.reason)
  }

  if (deploymentStatsResult.status === 'fulfilled') {
    deploymentStats.value = deploymentStatsResult.value
  } else {
    recordError('deploymentStats', deploymentStatsResult.reason)
  }

  if (incidentResult.status === 'fulfilled') {
    incidents.value = incidentResult.value.incidents
    incidentCount.value = incidentResult.value.count
  } else {
    recordError('incidents', incidentResult.reason)
  }

  if (incidentStatsResult.status === 'fulfilled') {
    incidentStats.value = incidentStatsResult.value
  } else {
    recordError('incidentStats', incidentStatsResult.reason)
  }

  if (issueResult.status === 'fulfilled') {
    issues.value = issueResult.value.issues
    issueCount.value = issueResult.value.count
  } else {
    recordError('issues', issueResult.reason)
  }

  loading.value = false
}

function askQuestion(question: string) {
  void router.push({ path: '/chat', query: { prompt: question, new: '1' } })
}

function formatDate(value: string) {
  return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

function formatDuration(seconds: number) {
  return `${Math.round(seconds)}s`
}

onMounted(loadOperations)
</script>

<template>
  <section class="mx-auto max-w-6xl">
    <header class="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">Operational context</p>
        <h1 class="mt-2 text-3xl font-semibold tracking-tight text-slate-100">Operations</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-400">A concise view of live engineering data, with questions you can take straight to MCPilot.</p>
      </div>
    </header>

    <div class="mb-8 grid gap-3 sm:grid-cols-3">
      <template v-if="loading">
        <div v-for="item in 3" :key="item" class="h-28 animate-pulse rounded-2xl bg-slate-900/80" />
      </template>
      <template v-else>
        <StatCard label="Repositories" :value="errors.repositories ? '—' : repositoryCount" detail="Returned by the API" />
        <StatCard label="Open incidents" :value="errors.incidentStats ? '—' : incidentStats?.open_incidents ?? 0" detail="From incident statistics" />
        <StatCard label="Deployment success" :value="errors.deploymentStats ? '—' : deploymentSuccessRate" detail="From returned deployment history" />
      </template>
    </div>

    <div class="space-y-6">
      <article class="operations-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Repositories</p>
            <h2 class="section-title">{{ repositoryCount }} repositories</h2>
            <p class="section-description">All repositories returned by FastAPI.</p>
          </div>
        </div>
        <RequestState
          :loading="loading"
          :error="errors.repositories || ''"
          :empty="displayedRepositories.length === 0"
          empty-message="No repositories returned."
          @retry="loadOperations"
        >
          <div class="grid gap-3 md:grid-cols-2">
            <div v-for="repository in displayedRepositories" :key="repository.name" class="record-card">
              <div class="flex items-start justify-between gap-3">
                <p class="font-medium text-slate-200">{{ repository.name }}</p>
                <span class="text-xs text-slate-500">{{ repository.visibility }}</span>
              </div>
              <p class="mt-2 text-xs text-slate-500">{{ repository.language || 'Language not provided' }} · {{ repository.team || 'Team not provided' }}</p>
            </div>
          </div>
        </RequestState>
        <div class="question-list" aria-label="Repository questions">
          <button v-for="question in suggestedQuestions.repositories" :key="question" type="button" class="question-chip" @click="askQuestion(question)">{{ question }}</button>
        </div>
      </article>

      <article class="operations-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Builds</p>
            <h2 class="section-title">{{ buildCount }} build runs</h2>
            <p class="section-description">All returned runs and the slowest feedback loops.</p>
          </div>
        </div>
        <RequestState
          :loading="loading"
          :error="errors.builds || ''"
          :empty="displayedBuilds.length === 0"
          empty-message="No build runs returned."
          @retry="loadOperations"
        >
          <div class="grid gap-6 lg:grid-cols-2">
            <div>
              <h3 class="subsection-title">All runs</h3>
              <div class="space-y-3">
                <div v-for="build in displayedBuilds" :key="`${build.repository}-${build.commit_id}-${build.started_at}`" class="record-row">
                  <div>
                    <p class="text-sm font-medium text-slate-200">{{ build.repository }}</p>
                    <p class="record-meta">Commit #{{ build.commit_id }} · {{ formatDate(build.started_at) }}</p>
                  </div>
                  <StatusBadge :value="build.status" />
                </div>
              </div>
            </div>
            <div>
              <h3 class="subsection-title">Slowest runs</h3>
              <div v-if="errors.slowestBuilds" class="text-sm text-rose-200" role="alert">{{ errors.slowestBuilds }}</div>
              <div v-else-if="slowestBuilds.length === 0" class="text-sm text-slate-500">No slow build data returned.</div>
              <div v-else class="space-y-3">
                <div v-for="build in slowestBuilds" :key="`${build.repository}-${build.commit_id}-${build.started_at}`" class="record-row">
                  <p class="text-sm text-slate-200">{{ build.repository }} <span class="text-xs text-slate-500">#{{ build.commit_id }}</span></p>
                  <span class="text-sm font-semibold tabular-nums text-teal-200">{{ formatDuration(build.duration_seconds) }}</span>
                </div>
              </div>
            </div>
          </div>
        </RequestState>
        <div class="question-list" aria-label="Build questions">
          <button v-for="question in suggestedQuestions.builds" :key="question" type="button" class="question-chip" @click="askQuestion(question)">{{ question }}</button>
        </div>
      </article>

      <article class="operations-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Deployments</p>
            <h2 class="section-title">{{ deploymentCount }} deployments</h2>
            <p class="section-description">All returned releases and delivery outcome.</p>
          </div>
        </div>
        <div v-if="errors.deploymentStats" class="mb-5 text-sm text-rose-200" role="alert">{{ errors.deploymentStats }}</div>
        <div v-else-if="deploymentStats" class="mb-5 flex flex-wrap gap-5 text-sm text-slate-400">
          <span><strong class="text-slate-100">{{ deploymentStats.successful_deployments }}</strong> successful</span>
          <span><strong class="text-slate-100">{{ deploymentStats.failed_deployments }}</strong> failed</span>
          <span><strong class="text-slate-100">{{ formatDuration(deploymentStats.average_duration_seconds) }}</strong> average</span>
        </div>
        <RequestState :loading="loading" :error="errors.deployments || ''" :empty="displayedDeployments.length === 0" empty-message="No deployments returned." @retry="loadOperations">
          <div class="space-y-3">
            <div v-for="deployment in displayedDeployments" :key="`${deployment.service}-${deployment.version}-${deployment.started_at}`" class="record-row">
              <div>
                <p class="text-sm font-medium text-slate-200">{{ deployment.service }} <span class="text-slate-500">{{ deployment.version }}</span></p>
                <p class="record-meta capitalize">{{ deployment.environment }} · {{ formatDate(deployment.started_at) }}</p>
              </div>
              <StatusBadge :value="deployment.status" />
            </div>
          </div>
        </RequestState>
        <div class="question-list" aria-label="Deployment questions">
          <button v-for="question in suggestedQuestions.deployments" :key="question" type="button" class="question-chip" @click="askQuestion(question)">{{ question }}</button>
        </div>
      </article>

      <article class="operations-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Incidents</p>
            <h2 class="section-title">{{ incidentCount }} incidents</h2>
            <p class="section-description">All returned incidents and current operational context.</p>
          </div>
        </div>
        <div v-if="errors.incidentStats" class="mb-5 text-sm text-rose-200" role="alert">{{ errors.incidentStats }}</div>
        <div v-else-if="incidentStats" class="mb-5 flex flex-wrap gap-5 text-sm text-slate-400">
          <span><strong class="text-slate-100">{{ incidentStats.open_incidents }}</strong> open</span>
          <span><strong class="text-slate-100">{{ incidentStats.resolved_incidents }}</strong> resolved</span>
          <span><strong class="text-slate-100">{{ formatDuration(incidentStats.average_resolution_time_seconds / 60) }}</strong> average resolution</span>
        </div>
        <RequestState :loading="loading" :error="errors.incidents || ''" :empty="displayedIncidents.length === 0" empty-message="No incidents returned." @retry="loadOperations">
          <div class="space-y-3">
            <div v-for="incident in displayedIncidents" :key="`${incident.service}-${incident.title}-${incident.detected_at}`" class="record-row items-start">
              <div>
                <p class="text-sm font-medium text-slate-200">{{ incident.title }}</p>
                <p class="record-meta">{{ incident.service }} · {{ formatDate(incident.detected_at) }}</p>
              </div>
              <StatusBadge :value="incident.severity" />
            </div>
          </div>
        </RequestState>
        <div class="question-list" aria-label="Incident questions">
          <button v-for="question in suggestedQuestions.incidents" :key="question" type="button" class="question-chip" @click="askQuestion(question)">{{ question }}</button>
        </div>
      </article>

      <article class="operations-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Issues</p>
            <h2 class="section-title">{{ issueCount }} issues</h2>
            <p class="section-description">All issues returned by the backend.</p>
          </div>
        </div>
        <RequestState :loading="loading" :error="errors.issues || ''" :empty="displayedIssues.length === 0" empty-message="No issues returned." @retry="loadOperations">
          <div class="grid gap-3 md:grid-cols-2">
            <div v-for="issue in displayedIssues" :key="`${issue.repository}-${issue.title}-${issue.created_at}`" class="record-card">
              <div class="flex items-start justify-between gap-3">
                <p class="text-sm font-medium text-slate-200">{{ issue.title }}</p>
                <StatusBadge :value="issue.priority" />
              </div>
              <p class="mt-2 text-xs text-slate-500">{{ issue.repository }} · {{ issue.assignee ? `Assigned to ${issue.assignee}` : 'Unassigned' }}</p>
            </div>
          </div>
        </RequestState>
        <div class="question-list" aria-label="Issue questions">
          <button v-for="question in suggestedQuestions.issues" :key="question" type="button" class="question-chip" @click="askQuestion(question)">{{ question }}</button>
        </div>
      </article>
    </div>
  </section>
</template>
