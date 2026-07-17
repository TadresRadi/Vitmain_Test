const REGENERATION_OPTION_KEY = 'regeneration_option'

export type RegenerationOption = 'new_business_info' | 'existing_business_info'

export function getRegenerationOption(): RegenerationOption | null {
  const value = localStorage.getItem(REGENERATION_OPTION_KEY)
  return value === 'new_business_info' || value === 'existing_business_info' ? value : null
}

export function setRegenerationOption(option: RegenerationOption): void {
  localStorage.setItem(REGENERATION_OPTION_KEY, option)
}

export function clearRegenerationOption(): void {
  localStorage.removeItem(REGENERATION_OPTION_KEY)
}
