// Replace images with your own or remote URLs.
// Keep ids URL-safe (used in /plaza/:id routes).
const topics = [
    {
      id: "climate-change",
      title: "Climate Change & Energy Transition",
      image:
        "https://images.unsplash.com/photo-1569163139394-de6e4e2e8c4e?q=80&w=1200&auto=format&fit=crop",
      facts: [
        "Global temperature rise continues with varying regional impacts and adaptation strategies.",
        "Renewable energy adoption rates differ significantly by country and economic capacity.",
        "Scientific consensus exists on causes, but policy approaches and timelines vary widely."
      ],
      chat: [
        {
          speaker: "Claire (Nature)",
          side: "left",
          text:
            "Latest climate models show we're approaching critical thresholds faster than previous estimates suggested."
        },
        {
          speaker: "Alice (WSJ)",
          side: "right",
          text:
            "Energy companies are reporting record investments in renewables, but fossil fuel demand remains strong."
        },
        {
          speaker: "Bob (Scientific American)",
          side: "left",
          text:
            "Adaptation strategies are becoming more urgent as extreme weather events increase in frequency and intensity."
        }
      ]
    },
    {
      id: "ai-safety",
      title: "AI Safety & Regulation",
      image:
        "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop",
      facts: [
        "Different jurisdictions are proposing distinct regulatory frameworks.",
        "Models are rapidly changing; timelines and capabilities evolve quickly.",
        "Independent evaluations and compute reporting are active policy topics."
      ],
      chat: [
        {
          speaker: "Leo (MIT Tech Review)",
          side: "left",
          text:
            "New evaluation proposals focus on dual-use risks and model reporting."
        },
        {
          speaker: "Rin (Financial Times)",
          side: "right",
          text:
            "Investors are weighing how rules could affect deployment speed and margins."
        },
        {
          speaker: "Zoe (Nature)",
          side: "left",
          text:
            "Researchers argue for standardized benchmarks so findings are comparable across labs."
        }
      ]
    },
    {
      id: "us-election",
      title: "U.S. Election",
      image:
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=1200&auto=format&fit=crop",
      facts: [
        "Turnout typically varies widely by state and demographic.",
        "Voting rules differ by state; deadlines matter.",
        "Polling averages can mask volatility; check margins of error."
      ],
      chat: [
        {
          speaker: "Kai (AP)",
          side: "left",
          text:
            "Latest tally shows small shifts in key counties after absentee counts."
        },
        {
          speaker: "Jules (FiveThirtyEight)",
          side: "right",
          text:
            "Model updates were minor; fundamentals still dominate the forecast."
        }
      ]
    }
  ];
  
  export default topics;
  