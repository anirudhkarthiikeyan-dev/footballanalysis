# Future Improvements

Ordered roughly by value-to-effort.

1. **European Performance module.** Source Champions League match data
   (e.g. football-data.co.uk also publishes a European CSV, or a
   dedicated Kaggle/GitHub CL dataset) for the 20 clubs named in the
   project brief, covering only each club's actual participation
   seasons. Add `dim_competition` and `fact_european_match` at the same
   grain as `FACT_MATCH`. Build the Domestic vs Europe comparison page.
2. **Compile the `.pbix`.** Follow `powerbi/README.md` in an
   environment with Power BI Desktop installed; commit the finished
   file (or a PDF export of the report pages, since `.pbix` binaries
   don't diff well in git).
3. **Team form / momentum measure in Power BI**, properly windowed with
   a "last N matches" table pattern rather than the simplified
   placeholder in `dax/measures.dax`.
4. **Playwright UI test suite** — automate the manual page-by-page
   browser verification done for this build (nav works, no console
   errors, no horizontal overflow) so it runs in CI.
5. **Clustering-based team/player archetypes** — a genuinely motivated
   addition to the ML layer (e.g. k-means over team attacking/defensive
   profiles) with the same rigor as the similarity model: a clear
   question, documented features, and evaluation.
6. **Deploy to Streamlit Community Cloud** and link the live URL from
   the README.
7. **Expand the learning log and interview prep** to the full topic
   list in the original project brief.
8. **Gameweek-level player data** (not just season totals) for a richer
   Player Explorer (form over the season, not just end-of-season
   aggregates) — the FPL archive has this in `gws/` per season.
