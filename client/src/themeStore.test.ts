import assert from "node:assert/strict";
import test from "node:test";

import { createThemeStore } from "./themeStore.ts";

// Minimal DOM stub for document.documentElement.dataset
function makeDomStub() {
  const dataset: Record<string, string> = {};
  return { dataset };
}

// Minimal localStorage stub
function makeStorageStub() {
  const store: Record<string, string> = {};
  return {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => {
      store[k] = v;
    },
  };
}

test('initial theme is "light" when no saved preference and media query is light', () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  const store = createThemeStore({ dom, storage, prefersDark: false });
  assert.equal(store.theme, "light");
  assert.equal(dom.dataset.theme, "light");
});

test('initial theme is "dark" when no saved preference and media query is dark', () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  const store = createThemeStore({ dom, storage, prefersDark: true });
  assert.equal(store.theme, "dark");
  assert.equal(dom.dataset.theme, "dark");
});

test("saved localStorage value overrides media query preference", () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  storage.setItem("theme", "dark");
  const store = createThemeStore({ dom, storage, prefersDark: false });
  assert.equal(store.theme, "dark");
  assert.equal(dom.dataset.theme, "dark");
});

test("toggleTheme flips theme from light to dark", () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  const store = createThemeStore({ dom, storage, prefersDark: false });
  store.toggleTheme();
  assert.equal(store.theme, "dark");
  assert.equal(dom.dataset.theme, "dark");
});

test("toggleTheme flips theme from dark to light", () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  const store = createThemeStore({ dom, storage, prefersDark: true });
  store.toggleTheme();
  assert.equal(store.theme, "light");
  assert.equal(dom.dataset.theme, "light");
});

test("toggleTheme persists new value to localStorage", () => {
  const dom = makeDomStub();
  const storage = makeStorageStub();
  const store = createThemeStore({ dom, storage, prefersDark: false });
  store.toggleTheme();
  assert.equal(storage.getItem("theme"), "dark");
});
