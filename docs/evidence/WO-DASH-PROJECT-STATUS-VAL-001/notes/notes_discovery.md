# Discovery notes

## client/src search: Project status
client/src/services/dashboardModulesApi.ts:43:export type ProjectStatusItem = {
client/src/services/dashboardModulesApi.ts:69:  getProjects(): Promise<ProjectStatusItem[]> {
client/src/services/dashboardModulesApi.ts:70:    return apiFetch<ProjectStatusItem[]>("/projects/mine");
client/src/pages/app/DashboardPage.tsx:8:import { ProjectStatusModule } from "../../components/dashboard/ProjectStatusModule";
client/src/pages/app/DashboardPage.tsx:97:          <ProjectStatusModule title={role === "developer" ? "Developer projects" : "Project status"} />
client/src/components/dashboard/ProjectStatusModule.tsx:3:import { dashboardModulesApi, type ProjectStatusItem } from "../../services/dashboardModulesApi";
client/src/components/dashboard/ProjectStatusModule.tsx:6:export const ProjectStatusModule = ({ title }: { title: string }) => {
client/src/components/dashboard/ProjectStatusModule.tsx:8:  const [projects, setProjects] = useState<ProjectStatusItem[]>([]);

## client/src search: api wiring
client/src/features/auth/AuthForms.tsx:56:    const oauthBase = `${API_BASE}/api/auth/oauth/${provider}/start`;
client/src/features/marketplace/MarketplaceShowcase.tsx:383:                      "project_status",
client/src/hooks/useOnboardingStatus.ts:3:import { getOnboardingStatus, type OnboardingStatus } from "../api/onboarding";
client/src/pages/onboarding/Trust.tsx:8:} from "../../api/onboarding";
client/src/pages/onboarding/Profile.tsx:4:import { completeOnboardingStep, updateOnboardingProfile } from "../../api/onboarding";
client/src/pages/onboarding/Checklist.tsx:8:} from "../../api/onboarding";
client/src/pages/onboarding/Welcome.tsx:4:import { startOnboarding } from "../../api/onboarding";
client/src/components/version/BuildBadge.tsx:16:    buildInfoPromise = fetch("/api/version", { cache: "no-store" })
client/src/services/dashboardModulesApi.ts:56:export const dashboardModulesApi = {
client/src/components/dashboard/AccountDetailsModule.tsx:3:import { dashboardModulesApi, type AccountDetails } from "../../services/dashboardModulesApi";
client/src/components/dashboard/AccountDetailsModule.tsx:29:      const data = await dashboardModulesApi.getAccountDetails();
client/src/components/dashboard/AccountDetailsModule.tsx:51:      const updated = await dashboardModulesApi.updateAccountDetails({
client/src/components/dashboard/PersonalInfoModule.tsx:3:import { dashboardModulesApi, type PersonalInfo } from "../../services/dashboardModulesApi";
client/src/components/dashboard/PersonalInfoModule.tsx:26:      const data = await dashboardModulesApi.getPersonalInfo();
client/src/components/dashboard/PersonalInfoModule.tsx:48:      const updated = await dashboardModulesApi.updatePersonalInfo(info);
client/src/components/dashboard/AccountBalanceModule.tsx:3:import { dashboardModulesApi, type AccountBalance } from "../../services/dashboardModulesApi";
client/src/components/dashboard/AccountBalanceModule.tsx:17:      const data = await dashboardModulesApi.getBalance();
client/src/components/dashboard/ProjectStatusModule.tsx:3:import { dashboardModulesApi, type ProjectStatusItem } from "../../services/dashboardModulesApi";
client/src/components/dashboard/ProjectStatusModule.tsx:17:      const data = await dashboardModulesApi.getProjects();

## Current endpoint
- Frontend calls `GET /projects/mine` via `dashboardModulesApi.getProjects()`.

## Verification update
- `npm ci` failed because there is no package-lock.json.
- `pnpm install --frozen-lockfile` failed due to an out-of-date pnpm-lock.yaml.
- Build previously ran after failed install because the pipeline lacked pipefail.
- Fix: refresh lockfile with `pnpm install --no-frozen-lockfile`, then frozen install + build.
- Evidence logs:
	- logs/pnpm_install.txt
	- logs/pnpm_build.txt
	- logs/pnpm_install_refresh_lock.txt
	- logs/pnpm_install_frozen_after_refresh.txt
	- logs/pnpm_build_after_refresh.txt
	- logs/pytest_after_lock_refresh.txt
client/src/components/dashboard/DeleteAccountModule.tsx:4:import { dashboardModulesApi } from "../../services/dashboardModulesApi";
client/src/components/dashboard/DeleteAccountModule.tsx:19:      const response = await dashboardModulesApi.deleteAccount();
