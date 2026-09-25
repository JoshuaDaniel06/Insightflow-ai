import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import "./index.css";

const API_URL = "http://127.0.0.1:8000";

const NAV_ITEMS = [
  {
    group: "MAIN",
    items: [
      { id: "overview", label: "Overview", icon: "▦" },
      { id: "customers", label: "Customers", icon: "♙" },
      { id: "analytics", label: "Analytics", icon: "◫" },
      { id: "ai", label: "AI Assistant", icon: "✦" },
    ],
  },
  {
    group: "INSIGHTS",
    items: [
      { id: "premium", label: "Premium Customers", icon: "◆" },
      { id: "top", label: "Top Customer", icon: "★" },
    ],
  },
  {
    group: "SYSTEM",
    items: [
      { id: "quality", label: "Data Quality", icon: "✓" },
      { id: "health", label: "API Health", icon: "●" },
    ],
  },
];

function getErrorMessage(error, fallback = "Something went wrong.") {
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error?.response?.status === 404) {
    return "The requested resource was not found.";
  }

  if (error?.response?.status >= 500) {
    return "Server error. Please check whether the backend is running.";
  }

  if (error?.code === "ERR_NETWORK") {
    return "Backend is offline. Start FastAPI with: uvicorn main:app --reload";
  }

  return fallback;
}

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "₹0";
  }

  return `₹${Number(value).toLocaleString("en-IN", {
    maximumFractionDigits: 0,
  })}`;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-IN");
}

function SkeletonCard() {
  return (
    <div className="metric-card skeleton-card">
      <div className="skeleton skeleton-small"></div>
      <div className="skeleton skeleton-large"></div>
      <div className="skeleton skeleton-medium"></div>
    </div>
  );
}

function LoadingTable() {
  return (
    <div className="table-card">
      <div className="table-loading">
        {[1, 2, 3, 4, 5].map((item) => (
          <div className="table-skeleton-row" key={item}>
            <div className="skeleton"></div>
            <div className="skeleton"></div>
            <div className="skeleton"></div>
            <div className="skeleton"></div>
            <div className="skeleton"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ title, message }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">⌁</div>
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState("overview");

  const [summary, setSummary] = useState(null);
  const [cities, setCities] = useState([]);
  const [cityAnalytics, setCityAnalytics] = useState(null);

  const [customers, setCustomers] = useState([]);
  const [customerTotal, setCustomerTotal] = useState(0);
  const [customerPage, setCustomerPage] = useState(1);
  const [customerTotalPages, setCustomerTotalPages] = useState(1);

  const [search, setSearch] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [segmentFilter, setSegmentFilter] = useState("");

  const [premiumCustomers, setPremiumCustomers] = useState([]);
  const [topCustomer, setTopCustomer] = useState(null);

  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const [question, setQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingCustomers, setLoadingCustomers] = useState(false);
  const [loadingCities, setLoadingCities] = useState(false);
  const [loadingPremium, setLoadingPremium] = useState(false);
  const [loadingTop, setLoadingTop] = useState(false);
  const [loadingCustomerDetails, setLoadingCustomerDetails] = useState(false);

  const [summaryError, setSummaryError] = useState("");
  const [customerError, setCustomerError] = useState("");
  const [analyticsError, setAnalyticsError] = useState("");
  const [premiumError, setPremiumError] = useState("");
  const [topError, setTopError] = useState("");

  const [apiHealth, setApiHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState("");

  const [dataQuality, setDataQuality] = useState(null);
  const [qualityLoading, setQualityLoading] = useState(false);
  const [qualityError, setQualityError] = useState("");

  const [lastUpdated, setLastUpdated] = useState(null);

  const loadSummary = async () => {
    setLoadingSummary(true);
    setSummaryError("");

    try {
      const response = await axios.get(
        `${API_URL}/analytics/summary`
      );

      setSummary(response.data?.data || null);
      setLastUpdated(new Date());
    } catch (error) {
      setSummaryError(
        getErrorMessage(
          error,
          "Unable to load dashboard analytics."
        )
      );
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadCities = async () => {
    setLoadingCities(true);
    setAnalyticsError("");

    try {
      const response = await axios.get(
        `${API_URL}/analytics/cities`
      );

      setCities(response.data?.data || []);
    } catch (error) {
      setAnalyticsError(
        getErrorMessage(
          error,
          "Unable to load city analytics."
        )
      );
    } finally {
      setLoadingCities(false);
    }
  };

  const loadCityAnalytics = async (city) => {
    if (!city) {
      setCityAnalytics(null);
      return;
    }

    setAnalyticsError("");

    try {
      const response = await axios.get(
        `${API_URL}/analytics/city/${encodeURIComponent(city)}`
      );

      setCityAnalytics(response.data?.data || null);
    } catch (error) {
      setCityAnalytics(null);
      setAnalyticsError(
        getErrorMessage(
          error,
          "Unable to load city details."
        )
      );
    }
  };

  const loadCustomers = async () => {
    setLoadingCustomers(true);
    setCustomerError("");

    try {
      const response = await axios.get(
        `${API_URL}/customers`,
        {
          params: {
            search,
            city: cityFilter,
            segment: segmentFilter,
            page: customerPage,
            page_size: 5,
          },
        }
      );

      const data = response.data;

      setCustomers(data?.data || []);
      setCustomerTotal(Number(data?.total || 0));
      setCustomerTotalPages(
        Number(data?.total_pages || 1)
      );

      if (data?.page && data.page !== customerPage) {
        setCustomerPage(data.page);
      }
    } catch (error) {
      setCustomers([]);
      setCustomerError(
        getErrorMessage(
          error,
          "Unable to load customers."
        )
      );
    } finally {
      setLoadingCustomers(false);
    }
  };

  const loadPremiumCustomers = async () => {
    setLoadingPremium(true);
    setPremiumError("");

    try {
      const response = await axios.get(
        `${API_URL}/analytics/premium-customers`
      );

      setPremiumCustomers(
        response.data?.customers || []
      );
    } catch (error) {
      setPremiumError(
        getErrorMessage(
          error,
          "Unable to load premium customers."
        )
      );
    } finally {
      setLoadingPremium(false);
    }
  };

  const loadTopCustomer = async () => {
    setLoadingTop(true);
    setTopError("");

    try {
      const response = await axios.get(
        `${API_URL}/analytics/top-customer`
      );

      setTopCustomer(response.data?.data || null);
    } catch (error) {
      setTopError(
        getErrorMessage(
          error,
          "Unable to load top customer."
        )
      );
    } finally {
      setLoadingTop(false);
    }
  };

  const loadHealth = async () => {
    setHealthLoading(true);
    setHealthError("");

    try {
      const response = await axios.get(
        `${API_URL}/health`
      );

      setApiHealth(response.data);
    } catch (error) {
      setApiHealth(null);
      setHealthError(
        getErrorMessage(
          error,
          "Unable to connect to API."
        )
      );
    } finally {
      setHealthLoading(false);
    }
  };

  const loadDataQuality = async () => {
    setQualityLoading(true);
    setQualityError("");

    try {
      /*
       * This uses the current customer table.
       * It intentionally does not recreate the historical
       * raw CSV quality numbers.
       */
      const response = await axios.get(
        `${API_URL}/customers`,
        {
          params: {
            page: 1,
            page_size: 100,
          },
        }
      );

      const rows = response.data?.data || [];

      let missingValues = 0;
      let invalidAges = 0;
      let invalidEmails = 0;

      rows.forEach((customer) => {
        if (
          customer.name === null ||
          customer.name === undefined ||
          String(customer.name).trim() === ""
        ) {
          missingValues++;
        }

        if (
          customer.city === null ||
          customer.city === undefined ||
          String(customer.city).trim() === ""
        ) {
          missingValues++;
        }

        if (
          customer.email === null ||
          customer.email === undefined ||
          String(customer.email).trim() === ""
        ) {
          missingValues++;
        }

        if (
          customer.age === null ||
          customer.age === undefined ||
          Number(customer.age) < 0 ||
          Number(customer.age) > 120
        ) {
          invalidAges++;
        }

        if (
          customer.email &&
          !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
            String(customer.email).trim()
          )
        ) {
          invalidEmails++;
        }
      });

      const emails = rows
        .map((customer) =>
          customer.email
            ? String(customer.email)
                .trim()
                .toLowerCase()
            : ""
        )
        .filter(Boolean);

      const duplicateEmails =
        emails.length -
        new Set(emails).size;

      setDataQuality({
        total_records:
          Number(response.data?.total || rows.length),
        missing_values: missingValues,
        invalid_ages: invalidAges,
        invalid_emails: invalidEmails,
        duplicate_emails: duplicateEmails,
      });
    } catch (error) {
      setDataQuality(null);
      setQualityError(
        getErrorMessage(
          error,
          "Unable to calculate data quality."
        )
      );
    } finally {
      setQualityLoading(false);
    }
  };

  const openCustomer = async (customerId) => {
    setLoadingCustomerDetails(true);

    try {
      const response = await axios.get(
        `${API_URL}/customer/${customerId}`
      );

      setSelectedCustomer(
        response.data?.customer || null
      );
    } catch (error) {
      setCustomerError(
        getErrorMessage(
          error,
          "Unable to load customer details."
        )
      );
    } finally {
      setLoadingCustomerDetails(false);
    }
  };

  const askAI = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setAiError("Please enter a question.");
      return;
    }

    setAiLoading(true);
    setAiError("");
    setAiAnswer("");

    try {
      const response = await axios.post(
        `${API_URL}/ask`,
        {
          question: trimmedQuestion,
        }
      );

      setAiAnswer(
        response.data?.answer ||
          "The AI assistant returned no answer."
      );
    } catch (error) {
      setAiError(
        getErrorMessage(
          error,
          "The AI assistant could not process your question."
        )
      );
    } finally {
      setAiLoading(false);
    }
  };

  const refreshCurrentPage = () => {
    if (activePage === "overview") {
      loadSummary();
      loadCities();
    }

    if (activePage === "customers") {
      loadCustomers();
    }

    if (activePage === "analytics") {
      loadSummary();
      loadCities();

      if (cityFilter) {
        loadCityAnalytics(cityFilter);
      }
    }

    if (activePage === "premium") {
      loadPremiumCustomers();
    }

    if (activePage === "top") {
      loadTopCustomer();
    }

    if (activePage === "quality") {
      loadDataQuality();
    }

    if (activePage === "health") {
      loadHealth();
    }
  };

  useEffect(() => {
    if (activePage === "overview") {
      loadSummary();
      loadCities();
    }

    if (activePage === "customers") {
      loadCustomers();
    }

    if (activePage === "analytics") {
      loadSummary();
      loadCities();
    }

    if (activePage === "premium") {
      loadPremiumCustomers();
    }

    if (activePage === "top") {
      loadTopCustomer();
    }

    if (activePage === "quality") {
      loadDataQuality();
    }

    if (activePage === "health") {
      loadHealth();
    }
  }, [activePage]);

  useEffect(() => {
    if (activePage !== "customers") {
      return;
    }

    loadCustomers();
  }, [
    customerPage,
    search,
    cityFilter,
    segmentFilter,
  ]);

  useEffect(() => {
    if (
      activePage === "analytics" &&
      cityFilter
    ) {
      loadCityAnalytics(cityFilter);
    }
  }, [cityFilter, activePage]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (activePage === "overview") {
        loadSummary();
        loadCities();
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [activePage]);

  const changePage = (page) => {
    setActivePage(page);

    if (page !== "customers") {
      setCustomerPage(1);
    }
  };

  const resetCustomerFilters = () => {
    setSearch("");
    setCityFilter("");
    setSegmentFilter("");
    setCustomerPage(1);
  };

  const renderHeader = () => {
    const titles = {
      overview: [
        "Overview",
        "Customer intelligence at a glance",
      ],
      customers: [
        "Customers",
        "Search, filter and explore your customer base",
      ],
      analytics: [
        "Analytics",
        "Understand customer revenue and city performance",
      ],
      ai: [
        "AI Assistant",
        "Ask questions about your customer data",
      ],
      premium: [
        "Premium Customers",
        "Customers with purchases between ₹10,000 and ₹14,999",
      ],
      top: [
        "Top Customer",
        "Your highest-value customer",
      ],
      quality: [
        "Data Quality",
        "Monitor the quality of the current customer dataset",
      ],
      health: [
        "API Health",
        "Monitor backend, database and RAG availability",
      ],
    };

    const [title, subtitle] =
      titles[activePage];

    return (
      <div className="page-header">
        <div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>

        <div className="header-actions">
          {lastUpdated && (
            <span className="last-updated">
              Updated{" "}
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}

          <button
            className="refresh-button"
            onClick={refreshCurrentPage}
          >
            ↻ Refresh
          </button>
        </div>
      </div>
    );
  };

  const renderOverview = () => {
    if (summaryError) {
      return (
        <>
          {renderHeader()}

          <div className="error-panel">
            <strong>Dashboard unavailable</strong>
            <p>{summaryError}</p>
            <button onClick={loadSummary}>
              Retry
            </button>
          </div>
        </>
      );
    }

    return (
      <>
        {renderHeader()}

        <section className="metrics-grid">
          {loadingSummary ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <div className="metric-card">
                <div className="metric-label">
                  TOTAL CUSTOMERS
                </div>
                <div className="metric-value">
                  {formatNumber(
                    summary?.total_customers ??
                      summary?.customer_count ??
                      0
                  )}
                </div>
                <div className="metric-description">
                  Active customer records
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  TOTAL REVENUE
                </div>
                <div className="metric-value">
                  {formatCurrency(
                    summary?.total_revenue ??
                      summary?.total_purchase ??
                      0
                  )}
                </div>
                <div className="metric-description">
                  Combined customer purchases
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  AVERAGE PURCHASE
                </div>
                <div className="metric-value">
                  {formatCurrency(
                    summary?.average_purchase ??
                      summary?.avg_purchase ??
                      0
                  )}
                </div>
                <div className="metric-description">
                  Average customer value
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  TOP CUSTOMER
                </div>
                <div className="metric-value metric-name">
                  {summary?.top_customer_name ||
                    summary?.top_customer?.name ||
                    topCustomer?.name ||
                    "—"}
                </div>
                <div className="metric-description">
                  Highest purchase value
                </div>
              </div>
            </>
          )}
        </section>

        <section className="dashboard-grid">
          <div className="panel chart-panel">
            <div className="panel-header">
              <div>
                <h2>Revenue by City</h2>
                <p>
                  Customer purchase distribution
                </p>
              </div>

              <button
                className="text-button"
                onClick={() =>
                  changePage("analytics")
                }
              >
                View analytics →
              </button>
            </div>

            {loadingCities ? (
              <div className="chart-skeleton skeleton"></div>
            ) : cities.length === 0 ? (
              <EmptyState
                title="No city data"
                message="There is currently no city analytics data available."
              />
            ) : (
              <div className="chart-container">
                <ResponsiveContainer
                  width="100%"
                  height={320}
                >
                  <BarChart data={cities}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="city"
                      tick={{ fontSize: 12 }}
                    />

                    <YAxis
                      tick={{ fontSize: 12 }}
                    />

                    <Tooltip
                      formatter={(value) =>
                        formatCurrency(value)
                      }
                    />

                    <Bar
                      dataKey="total_purchase"
                      name="Revenue"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="panel quick-panel">
            <div className="panel-header">
              <div>
                <h2>Quick Insights</h2>
                <p>Explore your data</p>
              </div>
            </div>

            <button
              className="quick-action"
              onClick={() =>
                changePage("customers")
              }
            >
              <span>♙</span>
              <div>
                <strong>Customer Directory</strong>
                <small>
                  Search and filter customers
                </small>
              </div>
              <span>→</span>
            </button>

            <button
              className="quick-action"
              onClick={() =>
                changePage("premium")
              }
            >
              <span>◆</span>
              <div>
                <strong>Premium Customers</strong>
                <small>
                  View high-value customers
                </small>
              </div>
              <span>→</span>
            </button>

            <button
              className="quick-action"
              onClick={() =>
                changePage("ai")
              }
            >
              <span>✦</span>
              <div>
                <strong>Ask AI</strong>
                <small>
                  Query your customer data
                </small>
              </div>
              <span>→</span>
            </button>

            <button
              className="quick-action"
              onClick={() =>
                changePage("quality")
              }
            >
              <span>✓</span>
              <div>
                <strong>Data Quality</strong>
                <small>
                  Check dataset quality
                </small>
              </div>
              <span>→</span>
            </button>
          </div>
        </section>
      </>
    );
  };

  const renderCustomers = () => (
    <>
      {renderHeader()}

      <div className="filter-card">
        <div className="filter-row">
          <div className="search-box">
            <span>⌕</span>
            <input
              type="text"
              placeholder="Search by ID, name or email..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setCustomerPage(1);
              }}
            />
          </div>

          <select
            value={cityFilter}
            onChange={(event) => {
              setCityFilter(event.target.value);
              setCustomerPage(1);
            }}
          >
            <option value="">
              All Cities
            </option>

            {cities.map((city) => (
              <option
                key={city.city}
                value={city.city}
              >
                {city.city}
              </option>
            ))}
          </select>

          <select
            value={segmentFilter}
            onChange={(event) => {
              setSegmentFilter(event.target.value);
              setCustomerPage(1);
            }}
          >
            <option value="">
              All Segments
            </option>
            <option value="Low Value">
              Low Value
            </option>
            <option value="Regular">
              Regular
            </option>
            <option value="Premium">
              Premium
            </option>
            <option value="High Value">
              High Value
            </option>
          </select>

          <button
            className="clear-filter-button"
            onClick={resetCustomerFilters}
          >
            Clear
          </button>
        </div>
      </div>

      {customerError && (
        <div className="inline-error">
          <span>{customerError}</span>
          <button onClick={loadCustomers}>
            Retry
          </button>
        </div>
      )}

      {loadingCustomers ? (
        <LoadingTable />
      ) : customers.length === 0 ? (
        <div className="panel">
          <EmptyState
            title="No customers found"
            message="Try changing your search or filter criteria."
          />
        </div>
      ) : (
        <div className="table-card">
          <div className="table-header">
            <div>
              <h2>Customer Directory</h2>
              <p>
                Showing {customers.length} of{" "}
                {formatNumber(customerTotal)} customers
              </p>
            </div>

            <span className="result-badge">
              Page {customerPage} /{" "}
              {customerTotalPages}
            </span>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Age</th>
                  <th>City</th>
                  <th>Email</th>
                  <th>Purchase</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.customer_id}>
                    <td>
                      <span className="customer-id">
                        {customer.customer_id}
                      </span>
                    </td>

                    <td>
                      <strong>
                        {customer.name}
                      </strong>
                    </td>

                    <td>{customer.age}</td>

                    <td>{customer.city}</td>

                    <td className="email-cell">
                      {customer.email || "—"}
                    </td>

                    <td>
                      <strong>
                        {formatCurrency(
                          customer.total_purchase
                        )}
                      </strong>
                    </td>

                    <td>
                      <button
                        className="view-button"
                        onClick={() =>
                          openCustomer(
                            customer.customer_id
                          )
                        }
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              disabled={customerPage <= 1}
              onClick={() =>
                setCustomerPage(
                  (page) => page - 1
                )
              }
            >
              ← Previous
            </button>

            <span>
              Page <strong>{customerPage}</strong>{" "}
              of{" "}
              <strong>
                {customerTotalPages}
              </strong>
            </span>

            <button
              disabled={
                customerPage >=
                customerTotalPages
              }
              onClick={() =>
                setCustomerPage(
                  (page) => page + 1
                )
              }
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {loadingCustomerDetails && (
        <div className="drawer-loading">
          Loading customer...
        </div>
      )}

      {selectedCustomer && (
        <div
          className="drawer-overlay"
          onClick={() =>
            setSelectedCustomer(null)
          }
        >
          <div
            className="customer-drawer"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="drawer-header">
              <div>
                <span className="drawer-label">
                  CUSTOMER PROFILE
                </span>

                <h2>
                  {selectedCustomer.name}
                </h2>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setSelectedCustomer(null)
                }
              >
                ×
              </button>
            </div>

            <div className="customer-profile">
              <div className="profile-avatar">
                {selectedCustomer.name
                  ?.charAt(0)
                  ?.toUpperCase()}
              </div>

              <div>
                <strong>
                  {selectedCustomer.name}
                </strong>
                <span>
                  {selectedCustomer.customer_id}
                </span>
              </div>
            </div>

            <div className="detail-list">
              <div>
                <span>Age</span>
                <strong>
                  {selectedCustomer.age}
                </strong>
              </div>

              <div>
                <span>City</span>
                <strong>
                  {selectedCustomer.city}
                </strong>
              </div>

              <div>
                <span>Email</span>
                <strong>
                  {selectedCustomer.email ||
                    "Not available"}
                </strong>
              </div>

              <div>
                <span>Total Purchase</span>
                <strong>
                  {formatCurrency(
                    selectedCustomer.total_purchase
                  )}
                </strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  const renderAnalytics = () => (
    <>
      {renderHeader()}

      {analyticsError && (
        <div className="inline-error">
          <span>{analyticsError}</span>
          <button
            onClick={() => {
              loadCities();

              if (cityFilter) {
                loadCityAnalytics(
                  cityFilter
                );
              }
            }}
          >
            Retry
          </button>
        </div>
      )}

      <section className="metrics-grid analytics-metrics">
        {loadingSummary ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <div className="metric-card">
              <div className="metric-label">
                CUSTOMERS
              </div>
              <div className="metric-value">
                {formatNumber(
                  summary?.total_customers ??
                    summary?.customer_count ??
                    0
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                REVENUE
              </div>
              <div className="metric-value">
                {formatCurrency(
                  summary?.total_revenue ??
                    summary?.total_purchase ??
                    0
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                AVG PURCHASE
              </div>
              <div className="metric-value">
                {formatCurrency(
                  summary?.average_purchase ??
                    summary?.avg_purchase ??
                    0
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                CITIES
              </div>
              <div className="metric-value">
                {cities.length}
              </div>
            </div>
          </>
        )}
      </section>

      <section className="dashboard-grid">
        <div className="panel chart-panel">
          <div className="panel-header">
            <div>
              <h2>Revenue by City</h2>
              <p>
                Compare customer purchase value
                across cities
              </p>
            </div>
          </div>

          {loadingCities ? (
            <div className="chart-skeleton skeleton"></div>
          ) : cities.length === 0 ? (
            <EmptyState
              title="No analytics available"
              message="City analytics could not be loaded."
            />
          ) : (
            <div className="chart-container">
              <ResponsiveContainer
                width="100%"
                height={350}
              >
                <BarChart data={cities}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis dataKey="city" />

                  <YAxis />

                  <Tooltip
                    formatter={(value) =>
                      formatCurrency(value)
                    }
                  />

                  <Bar
                    dataKey="total_purchase"
                    name="Revenue"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="panel city-insight-panel">
          <div className="panel-header">
            <div>
              <h2>City Analysis</h2>
              <p>
                Inspect one city in detail
              </p>
            </div>
          </div>

          <select
            className="full-select"
            value={cityFilter}
            onChange={(event) =>
              setCityFilter(event.target.value)
            }
          >
            <option value="">
              Select a city
            </option>

            {cities.map((city) => (
              <option
                key={city.city}
                value={city.city}
              >
                {city.city}
              </option>
            ))}
          </select>

          {cityAnalytics ? (
            <div className="city-stats">
              <div>
                <span>City</span>
                <strong>
                  {cityAnalytics.city}
                </strong>
              </div>

              <div>
                <span>Customers</span>
                <strong>
                  {formatNumber(
                    cityAnalytics.customer_count
                  )}
                </strong>
              </div>

              <div>
                <span>Total Purchase</span>
                <strong>
                  {formatCurrency(
                    cityAnalytics.total_purchase
                  )}
                </strong>
              </div>

              <div>
                <span>Average Purchase</span>
                <strong>
                  {formatCurrency(
                    cityAnalytics.average_purchase
                  )}
                </strong>
              </div>
            </div>
          ) : (
            <div className="mini-empty">
              Select a city to view detailed
              analytics.
            </div>
          )}
        </div>
      </section>
    </>
  );

  const renderAI = () => (
    <>
      {renderHeader()}

      <div className="ai-page">
        <div className="ai-hero">
          <div className="ai-icon">✦</div>

          <div>
            <h2>Customer Intelligence AI</h2>
            <p>
              Ask questions about your customer
              data using the RAG-powered assistant.
            </p>
          </div>
        </div>

        <div className="ai-question-card">
          <label>
            Ask a question
          </label>

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Example: Who is the highest-value customer?"
            maxLength={500}
          />

          <div className="ai-input-footer">
            <span>
              {question.length}/500
            </span>

            <button
              className="primary-button"
              onClick={askAI}
              disabled={aiLoading}
            >
              {aiLoading
                ? "Thinking..."
                : "Ask AI →"}
            </button>
          </div>
        </div>

        {aiError && (
          <div className="error-panel">
            <strong>AI request failed</strong>
            <p>{aiError}</p>
            <button onClick={askAI}>
              Retry
            </button>
          </div>
        )}

        {aiLoading && (
          <div className="ai-answer-card">
            <div className="skeleton skeleton-small"></div>
            <div className="skeleton skeleton-large"></div>
            <div className="skeleton skeleton-large"></div>
          </div>
        )}

        {!aiLoading && aiAnswer && (
          <div className="ai-answer-card">
            <div className="answer-header">
              <span>✦</span>
              <strong>AI Response</strong>
            </div>

            <div className="answer-content">
              {aiAnswer}
            </div>
          </div>
        )}

        <div className="suggested-questions">
          <h3>Try asking</h3>

          <div className="suggestion-grid">
            {[
              "Who is the highest-value customer?",
              "Which city has the highest revenue?",
              "How many customers do we have?",
              "What is the average purchase value?",
            ].map((item) => (
              <button
                key={item}
                onClick={() =>
                  setQuestion(item)
                }
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );

  const renderPremium = () => (
    <>
      {renderHeader()}

      {premiumError && (
        <div className="error-panel">
          <strong>
            Premium customer data unavailable
          </strong>
          <p>{premiumError}</p>
          <button
            onClick={loadPremiumCustomers}
          >
            Retry
          </button>
        </div>
      )}

      {loadingPremium ? (
        <LoadingTable />
      ) : premiumCustomers.length === 0 ? (
        <div className="panel">
          <EmptyState
            title="No premium customers"
            message="No customers currently match the premium segment."
          />
        </div>
      ) : (
        <div className="table-card">
          <div className="table-header">
            <div>
              <h2>Premium Customers</h2>
              <p>
                Customers with purchase values
                between ₹10,000 and ₹14,999
              </p>
            </div>

            <span className="result-badge">
              {premiumCustomers.length} customers
            </span>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Name</th>
                  <th>City</th>
                  <th>Purchase</th>
                </tr>
              </thead>

              <tbody>
                {premiumCustomers.map(
                  (customer) => (
                    <tr
                      key={
                        customer.customer_id
                      }
                    >
                      <td>
                        <span className="customer-id">
                          {
                            customer.customer_id
                          }
                        </span>
                      </td>

                      <td>
                        <strong>
                          {customer.name}
                        </strong>
                      </td>

                      <td>
                        {customer.city}
                      </td>

                      <td>
                        <strong>
                          {formatCurrency(
                            customer.total_purchase
                          )}
                        </strong>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );

  const renderTopCustomer = () => (
    <>
      {renderHeader()}

      {topError && (
        <div className="error-panel">
          <strong>
            Top customer unavailable
          </strong>
          <p>{topError}</p>
          <button onClick={loadTopCustomer}>
            Retry
          </button>
        </div>
      )}

      {loadingTop ? (
        <div className="top-customer-loading">
          <div className="skeleton skeleton-avatar"></div>
          <div className="skeleton skeleton-large"></div>
          <div className="skeleton skeleton-medium"></div>
        </div>
      ) : topCustomer ? (
        <div className="top-customer-layout">
          <div className="top-customer-card">
            <div className="top-crown">
              ★
            </div>

            <div className="top-avatar">
              {topCustomer.name
                ?.charAt(0)
                ?.toUpperCase()}
            </div>

            <h2>{topCustomer.name}</h2>

            <p>
              {topCustomer.customer_id}
            </p>

            <div className="top-purchase">
              {formatCurrency(
                topCustomer.total_purchase
              )}
            </div>

            <span>
              Highest customer purchase
            </span>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Customer Profile</h2>
                <p>
                  Highest-value customer
                  details
                </p>
              </div>
            </div>

            <div className="detail-list">
              <div>
                <span>Customer ID</span>
                <strong>
                  {topCustomer.customer_id}
                </strong>
              </div>

              <div>
                <span>Name</span>
                <strong>
                  {topCustomer.name}
                </strong>
              </div>

              <div>
                <span>City</span>
                <strong>
                  {topCustomer.city ||
                    "—"}
                </strong>
              </div>

              <div>
                <span>Total Purchase</span>
                <strong>
                  {formatCurrency(
                    topCustomer.total_purchase
                  )}
                </strong>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="panel">
          <EmptyState
            title="No top customer"
            message="No customer data is available."
          />
        </div>
      )}
    </>
  );

  const renderQuality = () => (
    <>
      {renderHeader()}

      {qualityError && (
        <div className="error-panel">
          <strong>
            Data quality check failed
          </strong>
          <p>{qualityError}</p>
          <button onClick={loadDataQuality}>
            Retry
          </button>
        </div>
      )}

      {qualityLoading ? (
        <section className="metrics-grid">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </section>
      ) : dataQuality ? (
        <>
          <section className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">
                TOTAL RECORDS
              </div>
              <div className="metric-value">
                {formatNumber(
                  dataQuality.total_records
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                MISSING VALUES
              </div>
              <div className="metric-value">
                {formatNumber(
                  dataQuality.missing_values
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                INVALID AGES
              </div>
              <div className="metric-value">
                {formatNumber(
                  dataQuality.invalid_ages
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                INVALID EMAILS
              </div>
              <div className="metric-value">
                {formatNumber(
                  dataQuality.invalid_emails
                )}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                DUPLICATE EMAILS
              </div>
              <div className="metric-value">
                {formatNumber(
                  dataQuality.duplicate_emails
                )}
              </div>
            </div>
          </section>

          <div className="panel quality-note">
            <h2>Data Quality Monitor</h2>

            <p>
              These metrics are calculated from the
              current MySQL customer table. They
              represent the current database state,
              not the original raw CSV ingestion
              history.
            </p>
          </div>
        </>
      ) : null}
    </>
  );

  const renderHealth = () => (
    <>
      {renderHeader()}

      {healthError && (
        <div className="error-panel">
          <strong>
            Backend connection failed
          </strong>
          <p>{healthError}</p>
          <button onClick={loadHealth}>
            Retry
          </button>
        </div>
      )}

      {healthLoading ? (
        <section className="health-grid">
          <div className="health-card">
            <div className="skeleton skeleton-small"></div>
            <div className="skeleton skeleton-large"></div>
          </div>

          <div className="health-card">
            <div className="skeleton skeleton-small"></div>
            <div className="skeleton skeleton-large"></div>
          </div>

          <div className="health-card">
            <div className="skeleton skeleton-small"></div>
            <div className="skeleton skeleton-large"></div>
          </div>
        </section>
      ) : apiHealth ? (
        <section className="health-grid">
          <div className="health-card">
            <div className="health-icon">
              ●
            </div>

            <div>
              <span>API STATUS</span>
              <strong>
                {apiHealth.status ||
                  "Unknown"}
              </strong>
            </div>
          </div>

          <div className="health-card">
            <div className="health-icon">
              ◉
            </div>

            <div>
              <span>DATABASE</span>
              <strong>
                {apiHealth.database ||
                  "Unknown"}
              </strong>
            </div>
          </div>

          <div className="health-card">
            <div className="health-icon">
              ✦
            </div>

            <div>
              <span>RAG</span>
              <strong>
                {apiHealth.rag ||
                  "Unknown"}
              </strong>
            </div>
          </div>
        </section>
      ) : (
        <div className="panel">
          <EmptyState
            title="No health information"
            message="Start the FastAPI backend and retry."
          />
        </div>
      )}

      <div className="panel system-info">
        <h2>Backend Information</h2>

        <div className="system-row">
          <span>API URL</span>
          <strong>{API_URL}</strong>
        </div>

        <div className="system-row">
          <span>Backend</span>
          <strong>FastAPI</strong>
        </div>

        <div className="system-row">
          <span>Database</span>
          <strong>MySQL</strong>
        </div>

        <div className="system-row">
          <span>AI / RAG</span>
          <strong>
            FAISS + Gemini
          </strong>
        </div>
      </div>
    </>
  );

  const renderPage = () => {
    switch (activePage) {
      case "customers":
        return renderCustomers();

      case "analytics":
        return renderAnalytics();

      case "ai":
        return renderAI();

      case "premium":
        return renderPremium();

      case "top":
        return renderTopCustomer();

      case "quality":
        return renderQuality();

      case "health":
        return renderHealth();

      case "overview":
      default:
        return renderOverview();
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            IAI
          </div>

          <div>
            <div className="brand-name">
               InsightFlow AI
            </div>

            <div className="brand-subtitle">
              AI CUSTOMER INTELLIGENCE
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((group) => (
            <div
              className="nav-group"
              key={group.group}
            >
              <div className="nav-group-title">
                {group.group}
              </div>

              {group.items.map((item) => (
                <button
                  key={item.id}
                  className={`nav-item ${
                    activePage === item.id
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    changePage(item.id)
                  }
                >
                  <span className="nav-icon">
                    {item.icon}
                  </span>

                  <span>
                    {item.label}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-dot"></div>

          <div>
            <strong>
              InsightFlow AI
            </strong>

            <span>
              Intelligence Platform v1.0
            </span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;