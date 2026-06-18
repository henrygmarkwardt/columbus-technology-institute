# Page Spec — Number Guessing Bench
---

## 1. Purpose & Placement

- A research page documenting the **Number Guessing Bench** — a benchmark testing whether
  LLMs produce genuinely random output.
- **File:** `number-guessing-bench.html` (root level, lowercase — matches site convention).
- **Linked from** `research.html` as the first real research entry (joins/replaces the
  current "No papers yet" placeholder).
- **Top nav:** stays out of the primary nav; lives only under Research. 

At the top of the page above the article should be this image: '/Users/henrymarkwardt/Downloads/ChatGPT Image Jun 18, 2026, 10_53_25 AM.png'
---

## 2. The Hook (lead with this)

> Which models are best at guessing *random* numbers?
> We created *Random Number Bench* to test this.

The page's emotional core is that one finding. Open with it plainly; let the surprise carry.

---

## 3. Design Principles (inherit the existing system — no new aesthetic)

see DESIGN.md, do NOT use the design conventions in number-guessing-bench/

---

## 4. Data & Assets

- **Source of truth:** '/Users/henrymarkwardt/Desktop/CIT/Number Guessing Bench/docs/results.json'


# Page Outline

> Top-to-bottom structure of `number-guessing-bench.html`. Reuses the standard page
> skeleton (head boilerplate, nav, footer, `script.js`). Edit/reorder/annotate below.

## Header / Nav
- Standard `.container` > `.nav` block (brand logo + nav links), identical to other pages.

## Main — `<section class="page">`

### 1. Title block
hook

### 2. The setup
We at the Columbus Technology Institute believe that solving *entropy* is the *key* to AGI. We assert that humanity won't have AGI until frontier models can succesfully *guess* a random number a *statistically significant* number of times.

We put leading Large Language Models (LLMs) to the test, picking a *random* number using our proprietary *random number generator* and then querying LLMs and *recording* the results.

We asked each LLM to guess a random number between 1 and 10, *100* times, and recorded the number of correct guesses, as well as the distrobution of *guesses*.

The figure below shows the results of our benchmark on *11* of the most frontier-frontier models.

### 3. The figure

A clean histogram with model on the x axis, # of correct guesses on the Y axis, ranked with the best guessers at the leftmost

This histogram should take inspiration from benchmarks that anthropic shows on there blog.


### 4. 

We found that most models guess correctly about *10%* of the time. This is inline with our expectations, but suggests we are still a long way away from *AGI*

The figure below shows the total distribution of guesses.

### 5. figure 2

A clean histogram with # of guesses on y axis and number on the x axis

Should be for the total of all the models

## 
We found that models guess *7* almost every time.

Do these models *know* something we don't? We at the Columbus Technology Institute don't think so -- if they did, we would expect to see *higher* correct guess totals.

We invite the community to test more models so we can saturate the benchmark. If you want to make a contribution, head over to our link<github>link.

---

# Research Page Change

- Replace the `.empty-note` placeholder (or add alongside it) with the first research entry
  linking to `number-guessing-bench.html`, it should have the hook. To the right of the hook should be this design: '/Users/henrymarkwardt/Downloads/ChatGPT Image Jun 18, 2026, 10_53_25 AM.png'
