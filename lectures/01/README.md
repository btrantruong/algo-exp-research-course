# Feed Ranking Lab

An offline classroom activity for discussing a simple feed-ranking algorithm.

## Open the demo

Open `feed-ranking-demo.html` in any modern web browser. It has no dependencies, build step, or network requirement. Each page includes a persistent lesson navigation bar, so students can move directly among Ranking, Features, and Predictions.

## Model

Each post receives the score:

```text
score = w × relevance + (1 − w) × popularity
```

The relevance weight `w` runs from 0.0 to 1.0 in increments of 0.1 and starts at 0.7.

| Post | Relevance | Popularity |
| --- | ---: | ---: |
| A | 9 | 2 |
| B | 7 | 6 |
| C | 4 | 10 |
| D | 6 | 4 |

At the default `w = 0.7`, the ranking is A, B, C, D. At `w = 0.0`, it becomes C, B, D, A.

## Classroom prompt

Ask students what behavior this objective may reward or suppress. For example: can popularity reward rage bait; can relevance-only ranking narrow exposure to new ideas; and what data or constraints would be needed to mitigate those effects?

## Second page: feature overlays

`feed-ranking-consequences.html` uses the same model and post scores, then places two illustrative post features directly beside each post name: whether the author is followed and an emotion label. Students can compare which features become common near the top at different values of `w`.

## Third page: learned predictions

`feed-ranking-model.html` visualizes six synthetic past interactions as a scatter plot, then shows how a simple linear model can estimate coefficients from those outcomes. It distinguishes observed inputs from learned coefficients and from the human-selected ranking weight `w`.
