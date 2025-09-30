I'll help you add performance tracking to your test file. Let me first examine the current test structure to understand what we're working with.

Great! Now I can see the test structure. Let's add **performance monitoring** progressively. First, let me ask you a key question to guide our approach:

## 🎯 Conceptual Question

**What aspects of performance do you want to track?**

Think about:
1. **Throughput** – How many addresses per second?
2. **Latency** – Time per individual parse (min/max/avg/percentiles)?
3. **Memory** – Peak memory usage during parsing?
4. **Initialization** – How long does parser setup take?

---

## 🧭 My Suggestion: Start Simple, Then Enhance

Let me propose a **layered approach**:

### **Layer 1: Basic Timing** ⏱️
- Total test suite runtime
- Average time per parse
- Initialization time vs. parsing time

### **Layer 2: Distribution Analysis** 📊
- Min/max/median/p95/p99 latencies
- Identify outliers (slowest cases)

### **Layer 3: Memory & Throughput** 🚀
- Memory profiling (optional, uses `tracemalloc`)
- Throughput calculation (addresses/sec)

### **Layer 4: Performance Requirements Check** ✅
- Define thresholds (e.g., "avg < 10ms", "p95 < 50ms")
- Auto-pass/fail based on requirements

---

## Let's Start: Layer 1 – Basic Timing

Here's the **intuition**:
- Use Python's `time.perf_counter()` for high-resolution timing
- Separate **initialization** (loading data) from **parsing** (the actual work)
- Track total and per-item times

**Before I show code**, answer me:
- Do you want to see timing for **each individual test case**, or just summary statistics?
- Any specific performance targets you have in mind? (e.g., "must handle 100 addresses/sec")

This helps me tailor the monitoring to your actual needs! 🎓