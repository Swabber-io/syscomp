import mesa

from .cell import Cell


class HexSnowflake(mesa.Model):
    """
    Represents the hex grid of cells. The grid is represented by a 2-dimensional array
    of cells with adjacency rules specific to hexagons.
    """

    def __init__(self, width=50, height=50):
        """
        Create a new playing area of (width, height) cells.
        """
        super().__init__()
        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = mesa.time.SimultaneousActivation(self)

        # Use a hexagonal grid, where edges wrap around.
        self.grid = mesa.space.HexSingleGrid(width, height, torus=True)

        # Place a dead cell at each location.
        for contents, pos in self.grid.coord_iter():
            cell = Cell(pos, self)
            self.grid.place_agent(cell, pos)
            self.schedule.add(cell)

        # activate the center(ish) cell.
        centerishCell = self.grid[width // 2][height // 2]

        centerishCell.state = 1
        for a in centerishCell.neighbors:
            a.isConsidered = True

        self.running = True

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        self.schedule.step()
