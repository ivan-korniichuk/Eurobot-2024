class DataAnaliser:
    def __init__(self, b_mid, y_mid, b_corner, y_corner, b_reserved, y_reserved):
        self.b_mid = b_mid
        self.y_mid = y_mid
        self.b_corner = b_corner
        self.y_corner = y_corner
        self.b_reserved = b_reserved
        self.y_reserved = y_reserved
        self.default_solar_pos = [0]*9

    def update (self, plants):
        print(len(plants))
        self.plants = plants
        # self.solar_panels = solar_panels



    def cluster_plants (self):
        non_assigned_plants = []
        b_mid_plants = []
        y_mid_plants = []
        b_corner_plants = []
        y_corner_plants = []
        b_reserved_plants = []
        y_reserved_plants = []


        for plant in self.plants:

            # for b_area in self.b_areas:
            #     if self.is_in_range(plant, b_area):
            #         b_plants.append(plant)
            #         break
            # # else:
            # #     continue

            # for y_area in self.y_areas:
            #     if self.is_in_range(plant, y_area):
            #         y_plants.append(plant)
            #         break
            # # else:
            # #     continue
            if self.is_in_range(plant, self.b_mid):
                b_mid_plants.append(plant)
                continue

            if self.is_in_range(plant, self.y_mid):
                y_mid_plants.append(plant)
                continue

            if self.is_in_range(plant, self.b_corner):
                b_corner_plants.append(plant)
                continue

            if self.is_in_range(plant, self.y_corner):
                y_corner_plants.append(plant)
                continue

            if self.is_in_range(plant, self.b_reserved):
                b_reserved_plants.append(plant)
                continue

            if self.is_in_range(plant, self.y_reserved):
                y_reserved_plants.append(plant)
                continue

            non_assigned_plants.append(plant)

        return [
            non_assigned_plants,
            b_mid_plants,
            y_mid_plants,
            b_corner_plants,
            y_corner_plants,
            b_reserved_plants,
            y_reserved_plants]

                
                
    def is_in_range (self, point, edges):
        if (min(edges[0][0], edges[1][0]) <= point[0] <= max(edges[0][0], edges[1][0]) 
            and min(edges[0][1], edges[1][1]) <= point[1] <= max(edges[0][1], edges[1][1])):

            return True
        return False
    
    # def save_default_solar_positions (self, solar_panels):
    #     for i in range(solar_panels):
    #         print(solar_panels[i])
    #         if solar_panels[i]:
    #             print(True)
    #             if self.default_solar_pos[i] == [0]:
    #                 self.default_solar_pos[i] = solar_panels[i]
    #             else:
    #                 self.default_solar_pos[i] = [//(def_pos+sol_pos)/2//]
    #     return
    
    # def analyse_solar_panels (self):
    #     self.solar_panels
    #     return