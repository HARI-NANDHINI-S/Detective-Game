import { useState } from "react";
import { useGame } from "../GameContext";
import { SCENES } from "../constants";
import Header from "../components/Header";

const PAGES = [
  [
    "GRAPH COLOURING",
    [
      [
        "What is graph colouring?",
        "A graph is a set of vertices joined by edges. Graph colouring asks: can we give every vertex one colour out of k colours, so that no edge joins two vertices of the same colour?",
      ],
      [
        "Suspects become vertices",
        "Each of the five suspects is one vertex. A vertex needs exactly one colour: a person can only be in one room at 22:40.",
      ],
      [
        "Locations become colours",
        "Gallery, Laboratory, Archive and Security Room are the four colours.",
      ],
      [
        "Edges are the restrictions",
        "An edge means these two were never in the same room — the colouring rule.",
      ],
      [
        "Evidence shrinks the domains",
        "Physical evidence removes a colour from a vertex. Edges + domains leave a single answer.",
      ],
    ],
  ],
  [
    "BACKTRACKING",
    [
      [
        "The idea",
        "Choose the next vertex, try a colour, recurse; if the branch dies, undo and try the next colour.",
      ],
      [
        "The events you see",
        "CHECK, ASSIGN, CONFLICT, BACKTRACK, SUCCESS — emitted by the same Python function that computes the answer.",
      ],
    ],
  ],
  [
    "FIVE MORE ALGORITHMS",
    [
      ["Binary Search", "Find the 22:40 alarm event in a sorted camera log in logarithmic probes."],
      ["Kruskal (MST)", "Cheapest cable network that still links every room; leftover links are blind spots."],
      ["0/1 Knapsack", "Spend a limited investigation budget for maximum evidence value."],
      ["Merge Sort", "Put case-file notes into chronological order, split and merge."],
      ["Dijkstra", "Fastest walk between two rooms — does an alibi's claimed time hold?"],
    ],
  ],
  [
    "COMPLEXITY",
    [
      ["Colouring", "Worst case O(V · k^V). k-colouring is NP-complete for k ≥ 3."],
      ["Binary search", "O(log n) comparisons on a sorted log."],
      ["Kruskal", "O(E log E) after sorting edges; Union-Find is nearly O(E)."],
      ["Knapsack", "O(nW) time and space for n leads and budget W."],
      ["Merge sort", "O(n log n) time, O(n) extra space."],
      ["Dijkstra", "O((V + E) log V) with a binary heap."],
    ],
  ],
];

export default function DaaScene() {
  const { setScene } = useGame();
  const [page, setPage] = useState(0);
  return (
    <div className="screen">
      <Header
        title="HOW THIS GAME SOLVES THE CASE"
        subtitle="Design and Analysis of Algorithms"
        right={<button onClick={() => setScene(SCENES.MENU)}>MENU</button>}
      />
      <div className="content">
        <div className="nav-row">
          {PAGES.map((p, i) => (
            <button key={p[0]} className={page === i ? "selected" : ""} onClick={() => setPage(i)}>
              {p[0]}
            </button>
          ))}
        </div>
        <div className="panel" style={{ marginTop: 16, minHeight: 420 }}>
          {PAGES[page][1].map(([h, b]) => (
            <div key={h} style={{ marginBottom: 18 }}>
              <div className="title-font gold" style={{ fontSize: 20 }}>
                {h}
              </div>
              <p>{b}</p>
            </div>
          ))}
        </div>
        <div className="nav-row">
          <button onClick={() => setScene(SCENES.BOARD)}>EVIDENCE BOARD</button>
          <button onClick={() => setScene(SCENES.ANALYSIS)}>RUN THE ALGORITHM</button>
        </div>
      </div>
    </div>
  );
}
