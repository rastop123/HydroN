import math

class WaterSNetwork:

    Q_POP_MID_DAILY = 0.200
    Q_CAR_MID_DAILY = 450
    Q_TRACTOR_MID_DAILY = 451
    Q_CASH_COW_MID_DAILY = 100  #КФ среднесуточного потребления на 1 ед
    Q_COW_MID_DAILY = 30

    K_DAILY_MAX = 1.2#КФ Суточной неравномерности
    K_DAILY_MIN = 0.8

    A_HOUR_MAX = 1.3
    A_HOUR_MIN = 0.5

    B_HOUR_MAX = ((750, 2.2), (1000, 2), (1500, 1.8), (2500, 1.6))
    B_HOUR_MIN = ((750, 0.07), (1000, 0.1), (1500, 0.1), (2500, 0.1))

    MID_TIME = 9
    alpha = 0.5
    SPEED = 0.7
    ke = 0.08
    sigma = 0.025 # уточнить
    q_poz = 0.010
    t_poz = 10 * 60

    def __init__(self,pop, q_shed, q_mft, yds, *args):
        self.pop = float(pop)
        self.q_shed = float(q_shed) / 1000
        self.q_mft = float(q_mft) / 1000
        self.l = args[0] # Передавать необходимо (0, l1, l2, ...)
        self.yds = float(yds)
        self.z = args[1]
        self.h_potr = args[2]

    def get_q_daily_mid(self):
        self.q_daily_mid = self.pop * self.Q_POP_MID_DAILY

    def get_q_daily_mn(self): #Уточнить по поводу Q
        self.q_daily_max = self.K_DAILY_MAX * self.q_daily_mid
        self.q_daily_min = self.K_DAILY_MIN * self.q_daily_mid

    def get_K_h(self):
        B_max = self.use_interpolate(self.pop, *self.B_HOUR_MAX)
        B_min = self.use_interpolate(self.pop, *self.B_HOUR_MIN)
        self.K_HOUR_MAX = self.A_HOUR_MAX * B_max
        self.K_HOUR_MIN = self.A_HOUR_MIN * B_min

    def get_q_hour_mn(self):
        self.q_hour_max = self.K_HOUR_MAX * (self.q_daily_max / 24)
        self.q_hour_min = self.K_HOUR_MIN * (self.q_daily_min / 24)
        self.q_hour_mid = self.q_daily_max / 24

    def get_time_mn(self):
        max = ((24 - self.MID_TIME) - (1 - self.K_HOUR_MAX)) / (self.K_HOUR_MAX - self.K_HOUR_MIN)
        min = 24 - self.MID_TIME - max
        self.t_max = round(max)
        self.t_min = round(min)

    def correct_q_hour(self):
        self.q_hour_max = (self.q_hour_mid * 24 - self.q_hour_min * self.t_min - self.q_hour_mid * self.MID_TIME) / self.t_max

    def get_q_mn(self):
        self.Q_max = self.q_hour_max / 3600
        self.Q_min = self.q_hour_min / 3600

    def get_q_yd(self):
        self.q_yd = self.Q_max / (self.l[5] + self.l[7] + self.l[9])

    def get_Q_pyt(self):
        self.Q_pyt23 = self.q_yd * self.l[5]
        self.Q_pyt34 = self.q_yd * self.l[7]
        self.Q_pyt45 = self.q_yd * self.l[9]

    def get_different_Q(self):
        self.Q_r30 = 0.5 * self.Q_pyt34
        self.Q_f30 = self.Q_r30
        self.Q_yz3 = 0
        self.Q_tr23 = self.Q_f30 # лучше узнать у преподователя
        self.Q_r23 = self.Q_yz3 + 0.5 * self.Q_pyt23 + self.Q_tr23
        self.Q_f23 = self.Q_yz3 + self.Q_pyt23 + self.Q_tr23
        self.Q_yz2 = self.q_mft
        self.Q_tr12 = self.Q_f23
        self.Q_r12 = self.Q_yz2 + self.Q_tr12
        self.Q_f12 = self.Q_r12
        self.Q_r40 = 0.5 * self.Q_pyt34
        self.Q_f40 = self.Q_r40
        self.Q_yz4 = 0
        self.Q_tr45 = self.Q_f40  # лучше узнать у преподователя
        self.Q_r45 = self.Q_yz4 + 0.5 * self.Q_pyt45 + self.Q_tr45
        self.Q_f45 = self.Q_yz4 + self.Q_pyt45 + self.Q_tr45
        self.Q_yz5 = self.q_shed
        self.Q_tr15 = self.Q_f45
        self.Q_r15 = self.Q_yz5 + self.Q_tr15
        self.Q_f15 = self.Q_r15
        self.Q_rl3 = self.Q_f12 + self.Q_f15

    def get_d(self):
        self.d30 = math.sqrt((4 * self.Q_r30) / (math.pi * self.SPEED))
        self.d40 = math.sqrt((4 * self.Q_r40) / (math.pi * self.SPEED))
        self.d12 = math.sqrt((4 * self.Q_r12) / (math.pi * self.SPEED))
        self.d45 = math.sqrt((4 * self.Q_r45) / (math.pi * self.SPEED))
        self.d15 = math.sqrt((4 * self.Q_r15) / (math.pi * self.SPEED))
        self.d23 = math.sqrt((4 * self.Q_r23) / (math.pi * self.SPEED))
        self.dl3 = math.sqrt((4 * self.Q_rl3) / (math.pi * self.SPEED))
        print('Диаметр равен:', self.d30)
        self.d30 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d40)
        self.d40 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d12)
        self.d12 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d45)
        self.d45 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d15)
        self.d15 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d23)
        self.d23 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.dl3)
        self.dl3 = float(input('Введите Диаметр по таблице:'))

    def link_a_ring(self):
        q = self.Q_r30 + self.Q_r40
        self.kt = self.ke + self.sigma * 25
        self.h_12 = self.calc_h(self.l[4], self.Q_r12, self.d12)
        self.h_23 = self.calc_h(self.l[5], self.Q_r23, self.d23)
        self.h_34 = self.calc_h(self.l[7], q, self.d30)
        self.h_45 = self.calc_h(self.l[9], self.Q_r45, self.d45)
        self.h_15 = self.calc_h(self.l[10], self.Q_r15, self.d15)
        y = (self.h_15 + self.h_45 - self.h_12 -self.h_23 -self.h_34) / (-2 * self.h_34)
        x = 1 - y
        self.Q_r30 = x * self.Q_pyt34
        self.Q_f30 = self.Q_r30
        self.Q_yz3 = 0
        self.Q_tr23 = self.Q_f30  # лучше узнать у преподователя
        self.Q_r23 = self.Q_yz3 + 0.5 * self.Q_pyt23 + self.Q_tr23
        self.Q_f23 = self.Q_yz3 + self.Q_pyt23 + self.Q_tr23
        self.Q_yz2 = self.q_mft
        self.Q_tr12 = self.Q_f23
        self.Q_r12 = self.Q_yz2 + self.Q_tr12
        self.Q_f12 = self.Q_r12
        self.Q_r40 = y * self.Q_pyt34
        self.Q_f40 = self.Q_r40
        self.Q_yz4 = 0
        self.Q_tr45 = self.Q_f40  # лучше узнать у преподователя
        self.Q_r45 = self.Q_yz4 + 0.5 * self.Q_pyt45 + self.Q_tr45
        self.Q_f45 = self.Q_yz4 + self.Q_pyt45 + self.Q_tr45
        self.Q_yz5 = self.q_shed
        self.Q_tr15 = self.Q_f45
        self.Q_r15 = self.Q_yz5 + self.Q_tr15
        self.Q_f15 = self.Q_r15
        self.Q_rl3 = self.Q_f12 + self.Q_f15
        self.d30 = math.sqrt((4 * self.Q_r30) / (math.pi * self.SPEED))
        self.d40 = math.sqrt((4 * self.Q_r40) / (math.pi * self.SPEED))
        self.d12 = math.sqrt((4 * self.Q_r12) / (math.pi * self.SPEED))
        self.d45 = math.sqrt((4 * self.Q_r45) / (math.pi * self.SPEED))
        self.d15 = math.sqrt((4 * self.Q_r15) / (math.pi * self.SPEED))
        self.d23 = math.sqrt((4 * self.Q_r23) / (math.pi * self.SPEED))
        self.dl3 = math.sqrt((4 * self.Q_rl3) / (math.pi * self.SPEED))
        print('Диаметр равен:', self.d30)
        self.d30 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d40)
        self.d40 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d12)
        self.d12 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d45)
        self.d45 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d15)
        self.d15 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d23)
        self.d23 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.dl3)
        self.dl3 = float(input('Введите Диаметр по таблице:'))

    def calc_watertower(self):
        self.Q_daily_max = self.Q_max * 3600 * 24 + self.q_mft * 3600 * 24 + self.q_shed * 3600 * 24
        self.V_r = 0.052 * self.Q_daily_max
        self.V_pz = self.q_poz * self.t_poz
        self.V_b = self.V_r + self.V_pz



    def calc_h(self, l, q, d):
        res = (0.009 * (self.kt ** 0.25) * l * (q ** 2)) / (d ** 5.25)
        return res

    def my_summ(self, *args):
        k = 0
        for i in args:
            k += i
        return k

    def use_interpolate(self, x, *rv):
        x = float(x)
        l = len(rv)
        for i in range(0, l):
            if x > rv[i][0]:
                if x <= rv[i + 1][0]:
                    final_value = rv[i][1] + ((x - rv[i][0]) / (rv[i + 1][0] - rv[i][0])) * (rv[i + 1][1] - rv[i][1])
                    return final_value
        else:
            pass

    def all_calc(self):
        self.get_q_daily_mid()
        self.get_q_daily_mn()
        self.get_K_h()
        self.get_q_hour_mn()
        self.get_time_mn()
        self.correct_q_hour()
        self.get_q_mn()
        self.get_q_yd()
        self.get_Q_pyt()
        self.get_different_Q()
        self.get_d()
        self.link_a_ring()