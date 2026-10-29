// Adapted from Watermelon UI Fund Widget's FundCard (MIT).
// https://registry.watermelon.sh/r/fund-widget.json
// Uses scroll progress instead of drag, with restrained rotation and progressive blur.
import { motion, useMotionTemplate, useReducedMotion, useTransform } from 'motion/react';

export default function ScrollResearchCard({ progress, index, children }) {
  const reduced = useReducedMotion();
  const center = index * .36 + .12;
  const stops = [center - .35, center - .12, center + .12, center + .35];
  const rotateX = useTransform(progress, stops, [14, 0, 0, -10]);
  const y = useTransform(progress, stops, [110, 0, 0, -95]);
  const scale = useTransform(progress, stops, [.87, 1, 1, 1.05]);
  const opacity = useTransform(progress, stops, [0, 1, 1, 0]);
  const blur = useTransform(progress, stops, [5, 0, 0, 5]);
  const filter = useMotionTemplate`blur(${blur}px)`;
  return <motion.div className="scroll-research-card" style={reduced ? {} : {
    rotateX, y, scale, opacity, filter, transformPerspective: 1200,
  }}>{children}</motion.div>;
}
