import { motion } from "framer-motion";
import ContactForm from "@/components/ContactForm";

const About = () => {
  return (
    <main className="min-h-screen bg-background pt-32 pb-20 px-4 md:px-6">
      <div className="container mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <h1 className="heading-display text-[clamp(3rem,10vw,10rem)] leading-[0.85] mb-8">
            About
          </h1>
          <p className="text-3xl md:text-4xl leading-relaxed max-w-3xl">
            MathMentor AI doesn't just give answers.
            <span className="text-primary"> It teaches the miss.</span>
          </p>
        </motion.div>

        {/* Description */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-3xl space-y-8 mb-32"
        >
          <p className="text-xl text-muted-foreground leading-relaxed">
            MathMentor AI is a math tutor that reviews your actual work. You
            pick a problem, write out your solution step by step, and it reads
            every line — finding the <span className="text-foreground">first place things went wrong</span>, naming the exact kind of mistake (a sign slip, a
            calculation error, a gap in the concept), explaining the fix, and
            showing the step you should have taken.
          </p>
          <p className="text-xl text-muted-foreground leading-relaxed">
            Most math apps hand you an answer, a video, or a vague hint and
            call it help. MathMentor AI works like a teacher with unlimited
            patience: it reads what <span className="text-foreground">you</span> wrote, diagnoses the specific
            error, and teaches the miss — not the topic in general. No answers
            without understanding. No passive watching.
          </p>
          <p className="text-xl text-muted-foreground leading-relaxed">
            For students, that means help that actually sticks. For teachers,
            it's leverage: students get step-level feedback the moment they're
            stuck, so class time goes to the questions only a human can answer.
            Every attempt feeds a living mastery profile — topic by topic,
            concept by concept — so practice always targets what needs work,
            not what's already mastered.
          </p>
          <p className="text-xl text-muted-foreground leading-relaxed">
            This is just the beginning: entering your own problems, richer
            progress tracking, and more are on the way. One place for all of
            it — from your first shaky equation to the hardest problem on the
            test.
          </p>
        </motion.div>

        {/* Project author and advisor */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="border-t border-border pt-20 mb-32"
        >
          <div className="grid grid-cols-12 gap-16 items-start">
            <div className="col-span-12 md:col-span-4">
              <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-4">
                Project team
              </span>
              <div className="w-28 h-28 rounded-full bg-secondary border border-border flex items-center justify-center">
                <span className="heading-display text-3xl text-muted-foreground">
                  ?
                </span>
              </div>
            </div>
            <div className="col-span-12 md:col-span-8 space-y-6">
              <h2 className="heading-display text-4xl md:text-5xl">
                Built by <span className="text-primary">Anchit Nayak.</span>
              </h2>
              <p className="text-xl text-muted-foreground leading-relaxed">
                Anchit Nayak is the author and student developer of MathMentor AI. The project combines mathematical reasoning, educational feedback design, AI-assisted diagnosis, progress analytics, and an accessible web experience.
              </p>
              <p className="text-sm text-muted-foreground/70 uppercase tracking-wider">
                Advisor: Dr. Qingyang Xiao
              </p>
            </div>
          </div>
        </motion.div>

        {/* Feedback & collaboration section */}
        <div className="grid grid-cols-12 gap-16 border-t border-border pt-20">
          <div className="col-span-12 md:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="mb-12"
            >
              <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-4">
                Feedback &amp; collaboration
              </span>
              <h2 className="heading-display text-4xl md:text-5xl">
                Tell us what to make better.{" "}
                <span className="text-primary">Or what to build next.</span>
              </h2>
            </motion.div>
            <ContactForm />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="col-span-12 md:col-span-5"
          >
            <div className="space-y-12">
              <div>
                <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-4">
                  Great things to send
                </span>
                <ul className="space-y-2 text-lg text-muted-foreground">
                  <li>• What's working — and what isn't</li>
                  <li>• Ideas for features you wish existed</li>
                  <li>• Bugs, rough edges, confusing moments</li>
                  <li>• Collaboration or business inquiries</li>
                </ul>
              </div>

              <div className="border-t border-border pt-12">
                <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-4">
                  Not sure what to write?
                </span>
                <p className="text-lg text-foreground">
                  Even one line helps. MathMentor AI gets better with every
                  message from the people actually using it —{" "}
                  <span className="text-primary">yours included.</span>
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
};

export default About;
