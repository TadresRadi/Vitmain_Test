import { beforeEach, describe, expect, it } from "vitest"
import {
  clearRegenerationOption,
  getRegenerationOption,
  setRegenerationOption,
} from "./regenerationFlowService"

describe("regenerationFlowService", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("stores and reads a valid regeneration option", () => {
    setRegenerationOption("existing_business_info")

    expect(getRegenerationOption()).toBe("existing_business_info")
  })

  it("returns null for missing or unknown options", () => {
    expect(getRegenerationOption()).toBeNull()

    localStorage.setItem("regeneration_option", "unexpected")

    expect(getRegenerationOption()).toBeNull()
  })

  it("clears the regeneration option", () => {
    setRegenerationOption("new_business_info")
    clearRegenerationOption()

    expect(getRegenerationOption()).toBeNull()
  })
})
