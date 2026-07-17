import { beforeEach, describe, expect, it, vi } from "vitest"

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock("@/lib/axios", () => ({
  default: apiMock,
  api: apiMock,
}))

describe("onboardingService", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("fetches the current onboarding response", async () => {
    const data = { business_name: "Vitamin" }
    apiMock.get.mockResolvedValueOnce({ data })

    const { getOnboarding } = await import("./onboardingService")

    await expect(getOnboarding()).resolves.toBe(data)
    expect(apiMock.get).toHaveBeenCalledWith("/onboarding/")
  })

  it("maps the form model to the backend payload", async () => {
    const data = { message: "ok" }
    apiMock.post.mockResolvedValueOnce({ data })

    const { saveOnboarding } = await import("./onboardingService")

    await expect(
      saveOnboarding({
        createNew: true,
        data: {
          businessName: "Vitamin",
          governorate: "Cairo",
          businessType: "restaurant",
          businessSubtype: "",
          businessTypeOther: "",
          marketingGoals: ["sales", "awareness"],
          targetAudience: "families",
          targetAudienceOther: "",
          toneOfVoice: "friendly",
          toneOfVoiceOther: "",
        },
      }),
    ).resolves.toBe(data)

    expect(apiMock.post).toHaveBeenCalledWith("/onboarding/", {
      business_name: "Vitamin",
      governorate: "Cairo",
      business_type: "restaurant",
      business_subtype: null,
      business_type_other: null,
      marketing_goals: ["sales", "awareness"],
      target_audience: "families",
      target_audience_other: null,
      tone_of_voice: "friendly",
      tone_of_voice_other: null,
      create_new: true,
    })
  })
})
