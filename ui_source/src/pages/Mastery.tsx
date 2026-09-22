import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  LEVELS,
  getTopics,
  setTopicLevel,
  type Level,
  type TopicMastery,
} from "@/data/mastery";

const pct = (value: number) => `${Math.round(value * 100)}%`;

const MasteryBar = ({ value }: { value: number }) => (
  <div className="h-1.5 w-full border border-border bg-background">
    <div
      className="h-full bg-primary transition-all"
      style={{ width: `${Math.max(2, value * 100)}%` }}
    />
  </div>
);

const TopicRow = ({
  topic,
  onLevel,
}: {
  topic: TopicMastery;
  onLevel: (level: Level) => void;
}) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-border bg-secondary/50">
      <div className="p-5 md:p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
          <Button
            type="button"
            variant="ghost"
            onClick={() => setOpen((current) => !current)}
            className="group h-auto gap-3 p-0 text-left hover:bg-transparent"
            aria-expanded={open}
          >
            <ChevronDown
              className={`h-5 w-5 text-muted-foreground transition-transform ${
                open ? "rotate-180 text-primary" : ""
              }`}
            />
            <span className="heading-display text-xl transition-colors group-hover:text-primary">
              {topic.name}
            </span>
            {topic.weak && (
              <span className="text-xs uppercase tracking-wider text-destructive">
                Weak
              </span>
            )}
          </Button>

          <div className="flex flex-wrap items-center gap-4 md:gap-6">
            <span className="text-sm text-muted-foreground">
              Mastery{" "}
              <span className="text-foreground">{topic.mastery.toFixed(2)}</span>
            </span>
            <div className="flex border border-border" aria-label={`${topic.name} starting level`}>
              {LEVELS.map((level) => (
                <Button
                  key={level}
                  type="button"
                  variant="ghost"
                  onClick={() => onLevel(level)}
                  className={`h-auto rounded-none px-3 py-1.5 text-xs uppercase tracking-wider hover:bg-secondary ${
                    topic.level === level
                      ? "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground"
                      : "text-muted-foreground hover:text-primary"
                  }`}
                >
                  {level}
                </Button>
              ))}
            </div>
          </div>
        </div>

        <MasteryBar value={topic.mastery} />
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-1 text-xs uppercase tracking-wider text-muted-foreground">
          <span>Attempts: {topic.attempts}</span>
          <span>Error rate: {pct(topic.errorRate)}</span>
          <span>Avg difficulty: {topic.avgDifficulty.toFixed(1)}</span>
        </div>
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden border-t border-border"
          >
            <div className="space-y-5 bg-background/40 p-5 md:p-6">
              <span className="text-xs uppercase tracking-wider text-muted-foreground">
                Concept mastery
              </span>
              {topic.concepts.map((concept, index) => (
                <motion.div
                  key={concept.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.05 * index }}
                >
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="text-base text-foreground">
                      {concept.name}
                      {concept.weak && (
                        <span className="ml-3 text-xs uppercase tracking-wider text-destructive">
                          Weak
                        </span>
                      )}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {concept.mastery.toFixed(2)}
                    </span>
                  </div>
                  <MasteryBar value={concept.mastery} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const Mastery = () => {
  const [topics, setTopics] = useState(() => getTopics());
  const changeLevel = (topicId: string, level: Level) =>
    setTopics([...setTopicLevel(topicId, level)]);

  return (
    <main className="min-h-screen bg-background px-4 pb-20 pt-32 md:px-6">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <h1 className="heading-display mb-8 text-[clamp(3rem,10vw,10rem)] leading-[0.85]">
            Mastery
          </h1>
          <p className="max-w-2xl text-xl text-muted-foreground">
            See your progress by topic, choose a starting level, and open any
            topic for a concept-by-concept view.
          </p>
        </motion.div>

        <section className="max-w-4xl">
          <p className="mb-8 max-w-2xl text-muted-foreground">
            Everything starts at beginner. Your scores grow as you solve harder
            problems with fewer step errors.
          </p>
          <div className="space-y-4">
            {topics.map((topic) => (
              <TopicRow
                key={topic.id}
                topic={topic}
                onLevel={(level) => changeLevel(topic.id, level)}
              />
            ))}
          </div>
          <p className="mt-8 text-sm text-muted-foreground">
            Topic and concept names are placeholders until the real catalogue is connected.
          </p>
        </section>
      </div>
    </main>
  );
};

export default Mastery;