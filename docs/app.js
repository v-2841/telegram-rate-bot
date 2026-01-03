"use strict";

const symbols = ["USD", "EUR", "RUB", "AMD", "CNY"];
const wow = "59d54f5a2fd34f0991773bf43f378cef";
const apiUrl =
  "https://openexchangerates.org/api/latest.json?app_id=" +
  encodeURIComponent(wow || "") +
  "&symbols=" +
  encodeURIComponent(symbols.join(","));

const amountEl = document.getElementById("amount");
const fromEl = document.getElementById("from");
const toEl = document.getElementById("to");
const resultEl = document.getElementById("result");
const rateEl = document.getElementById("rate");
const statusEl = document.getElementById("status");
const updatedEl = document.getElementById("updated");
const refreshEl = document.getElementById("refresh");
const swapEl = document.getElementById("swap");

const state = {
  rates: null,
  updatedAt: null,
};

const numberFormatter = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
});

const rateFormatter = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 6,
});

function populateSelect(select, selectedValue) {
  select.innerHTML = "";
  for (const symbol of symbols) {
    const option = document.createElement("option");
    option.value = symbol;
    option.textContent = symbol;
    if (symbol === selectedValue) {
      option.selected = true;
    }
    select.appendChild(option);
  }
}

function setStatus(message) {
  statusEl.textContent = message;
}

function setUpdatedAt(date) {
  if (!date) {
    updatedEl.textContent = "Последнее обновление: -";
    return;
  }
  updatedEl.textContent = `Последнее обновление: ${date.toLocaleString("ru-RU")}`;
}

function normalizeAmount(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) {
    return 0;
  }
  return parsed;
}

function getRate(symbol) {
  if (!state.rates) {
    return null;
  }
  if (symbol === "USD") {
    return 1;
  }
  return state.rates[symbol] ?? null;
}

function convert(amount, from, to) {
  const fromRate = getRate(from);
  const toRate = getRate(to);
  if (!fromRate || !toRate) {
    return null;
  }
  const usdAmount = amount / fromRate;
  return usdAmount * toRate;
}

function updateResult() {
  const amount = normalizeAmount(amountEl.value);
  const from = fromEl.value;
  const to = toEl.value;
  const value = convert(amount, from, to);
  const rateValue = convert(1, from, to);

  if (value === null || rateValue === null) {
    resultEl.textContent = "-";
    rateEl.textContent = "Курс: -";
    return;
  }

  resultEl.textContent = `${numberFormatter.format(value)} ${to}`;
  rateEl.textContent = `Курс: 1 ${from} = ${rateFormatter.format(rateValue)} ${to}`;
}

async function fetchRates() {
  setStatus("Загружаю курсы...");
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    if (!data || !data.rates) {
      throw new Error("Missing rates data");
    }
    state.rates = data.rates;
    const updated = data.timestamp
      ? new Date(data.timestamp * 1000)
      : data.date
        ? new Date(`${data.date}T00:00:00Z`)
        : new Date();
    state.updatedAt = updated;
    setUpdatedAt(updated);
    setStatus("Курсы обновлены");
    updateResult();
  } catch (error) {
    setStatus("Не удалось загрузить курсы. Попробуйте еще раз.");
    setUpdatedAt(null);
    resultEl.textContent = "-";
    rateEl.textContent = "Курс: -";
  }
}

function swapCurrencies() {
  const from = fromEl.value;
  const to = toEl.value;
  fromEl.value = to;
  toEl.value = from;
  updateResult();
}

populateSelect(fromEl, "USD");
populateSelect(toEl, "RUB");

amountEl.addEventListener("input", updateResult);
fromEl.addEventListener("change", updateResult);
toEl.addEventListener("change", updateResult);
refreshEl.addEventListener("click", fetchRates);
swapEl.addEventListener("click", swapCurrencies);

fetchRates();
