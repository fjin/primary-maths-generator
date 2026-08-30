const TOPIC_LABELS = {
  mixed: "Mixed Topics",
  fractions: "Fractions",
  money: "Money",
  number_patterns: "Number Patterns",
  number_system: "Number System",
  time: "Time & Date",
  word_problems: "Word Problems",
};

const container = document.querySelector("#topic-subtopic-list");

loadTopics();

async function loadTopics() {
  try {
    const response = await fetch("data/question_bank.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Question bank returned ${response.status}`);
    }

    const questions = await response.json();
    renderTopics(groupTopics(questions));
  } catch (error) {
    container.classList.add("warning");
    container.textContent =
      "Could not load topics. Open this page through GitHub Pages or a local web server.";
    console.error(error);
  }
}

function groupTopics(questions) {
  const groups = new Map();
  for (const question of questions) {
    if (!question?.topic) {
      continue;
    }
    const topic = question.topic;
    const subtopic = question.subtopic || "general";
    if (!groups.has(topic)) {
      groups.set(topic, new Set());
    }
    groups.get(topic).add(subtopic);
  }

  return [...groups.entries()]
    .map(([topic, subtopics]) => ({
      topic,
      subtopics: [...subtopics].sort(),
    }))
    .sort((left, right) => left.topic.localeCompare(right.topic));
}

function renderTopics(groups) {
  container.innerHTML = "";

  const mixedCard = createTopicCard({
    topic: "mixed",
    subtopics: ["all"],
    note: "Use this to sample across every available topic.",
  });
  container.append(mixedCard);

  for (const group of groups) {
    container.append(createTopicCard(group));
  }
}

function createTopicCard({ topic, subtopics, note }) {
  const card = document.createElement("section");
  card.className = "topic-card";

  const title = document.createElement("h3");
  title.textContent = TOPIC_LABELS[topic] || titleCase(topic);

  const command = document.createElement("code");
  command.textContent = `--topic ${topic}`;

  const subtopicList = document.createElement("div");
  subtopicList.className = "subtopic-chip-list";

  for (const subtopic of subtopics) {
    const chip = document.createElement("code");
    chip.className = "subtopic-chip";
    chip.textContent = subtopic === "all" ? "--subtopic all" : subtopic;
    subtopicList.append(chip);
  }

  card.append(title, command);
  if (note) {
    const noteText = document.createElement("p");
    noteText.textContent = note;
    card.append(noteText);
  }
  card.append(subtopicList);
  return card;
}

function titleCase(value) {
  return String(value)
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
