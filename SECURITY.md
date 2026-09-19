# Security & privacy

This is a classroom game, not a gradebook. The design goal is narrow and
deliberate: **make it impossible for this app to accumulate a record about an
identifiable student.**

Everything below follows from that.

---

## One-time setup (≈5 minutes, in the Firebase console)

Until you do these, the app will not work at all — pages will show
"Couldn't sign in."

**1. Turn on sign-in.**
Console → **Authentication** → *Get started* → **Sign-in method**:

- enable **Anonymous** — this is what students get. No prompt, no password, no
  email. It hands the browser a random id so the rules can tell one device from
  another.
- enable **Google** — this is for you, and only you.

Then, same section → **Settings** → **Authorized domains** → add
`greymonroe.github.io`. The Google popup is blocked on any domain not listed;
`localhost` is allowed by default, the Pages URL is not. (Anonymous sign-in is
unaffected by this list — students are fine either way.)

**2. Publish the rules.**
Console → **Realtime Database** → **Rules** tab. Replace whatever is there with
the contents of [`database.rules.json`](database.rules.json), then **Publish**.

> The database was originally created in *Test mode*, which is open read/write
> to anyone on the internet. Publishing these rules is what closes it.

**3. Claim host.**
Open `index.html` (locally or on Pages), click **Sign in as host**, pick your
Google account. The first Google sign-in writes your uid to `admin/hostUid` and
that path then becomes immutable from the browser. Do this before you show the
app to a class.

To move host to a different account later, edit `admin/hostUid` by hand in the
console's **Data** tab.

---

## What the rules actually enforce

Rules run on Firebase's servers, so these hold no matter what a page's
JavaScript is edited to do.

| | |
|---|---|
| Unauthenticated reads | Nothing, except poll/quiz **question text**. |
| A student can read | Their own player record and their own answers. Nothing about anyone else. |
| A student can write | Their own nickname (≤ 20 chars), and **one** answer per question — write-once, enforced server-side, not by localStorage. |
| Answer timestamps | `serverTimestamp()`, validated as `ts === now`. The speed bonus is measured by Firebase's clock, so it can't be forged from a phone. |
| Scores | Host-written only. `players/<uid>/score` rejects a write from the student it belongs to. |
| The answer key | Lives at `quizzes/<id>/key`, readable by the host alone. Player phones download question text and options only; the correct index is published into `state.correct` at reveal time, after answers are locked. |
| Deleting anything | Host only. |

## What the database ever holds about a person

A nickname the student typed, a score, and which option they tapped — keyed to a
**random anonymous Firebase uid** that isn't linked to a Google account, an
email, a UC Davis identity, or anything else.

And it holds that only between "join" and the end of the game:

- **Finish** writes an anonymous results map (`uid → {rank, score}`, no names)
  and then erases `players` and `answers` outright. The final leaderboard on the
  big screen is rendered from the host browser's memory — closing the tab is the
  last copy gone.
- **Opening the host page** on a roster older than 6 hours erases it first, so
  nothing survives from a previous class.
- **Erase all player names** on `index.html` wipes every quiz's roster at once.
  It shouldn't ever be needed; it's there so "nothing is retained" is something
  you can enforce and verify in one click.

Poll responses (`submit.html`) carry no identity field at all — never have.

## Why it's built this way

The thing worth avoiding is a third-party service holding something that looks
like an education record: a named student, tied to performance, **maintained**
over time. That's the combination that pulls in FERPA and, at UC, the review
process that comes with student-record-level data on a non-campus system.

Break any one link and the problem goes away. This app breaks all three —
nicknames instead of names, an anonymous uid instead of an identity, and
erasure at the end of every game instead of retention.

**The corollary is the important part: nothing in here is graded.** If a score
needs to count toward a grade, it goes through Canvas or the campus-licensed
clicker system, where student records are supposed to live. Use this for the
fun, ungraded, in-class version — that's what it's good at.

## Known limits (stated plainly)

- **Nicknames are self-reported.** A student can type their full name if they
  want to. The prompt asks them not to, and whatever they type is erased at the
  end of the game — but nothing stops them.
- **Quiz and poll ids are create-only, not authenticated.** `newquiz.py` /
  `newpoll.py` write over plain REST with no credential. Anyone who knows the
  database URL could create a *new* poll. They cannot overwrite, read, or delete
  an existing one. This is the price of keeping the agent workflow a one-liner.
- **Question text is public.** Anyone with a quiz id can read the questions and
  options. The answer key is not public.
- **Anonymous uids are per-browser.** Clearing site data makes a student "new" —
  they'd rejoin with a score of 0. Fine for a game; not something to grade on.
- **Free "Spark" plan caps at 100 simultaneous connections.** A full lecture is
  fine; two live sessions at once might not be.

## If something changes

If this ever grows a feature that stores a real name, links to a UC Davis login,
or keeps scores between sessions, the reasoning above stops holding and it needs
a fresh look before it points at a class.
