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
    ke = 0.02
    sigma = 0.005 # уточнить
    q_poz = 0.010
    t_poz = 10 * 60
    g = 9.81
    Re_kr = 2300

    def __init__(self,pop, q_shed, q_mft, yds, *args):
        self.pop = float(pop)
        self.q_shed = float(q_shed) / 1000
        self.q_mft = float(q_mft) / 1000
        self.l = args[0] # Передавать необходимо (0, l1, l2, ...)
        self.yds = float(yds)
        self.z = args[1]
        self.h_potr = args[2]
        self.Q_r = {}
        self.Q_f = {}
        self.Q_tr = {}
        self.x_h = 0.5
        self.y_h = 0.5
        self.Q_yz = {}
        self.Q_yz['2'] = self.q_mft
        self.Q_yz['5'] = self.q_shed
        self.slossh = {}
        self.bind = ((3, 6, 1), (4, 1, 2), (5, 2, 3), (7, 3, 4), (9, 4, 5), (10, 5, 1))
        self.ring = [[4, 1, 2, -1], [5, 2, 3, -1], [7, 3, 4, -1], [9, 4, 5, 1], [10, 5, 1, 1]]
        self.lpyt = [5, 7, 9]
        self.knot_1 = [0, 1, 2, 3]
        self.knot_2 = [0, 1, 5, 4]
        self.ring_1 = [[4, 1, 2], [5, 2, 3], [7, 3, 0]]
        self.ring_2 = [[7, 0, 4], [9, 4, 5], [10, 5, 1]]
        self.itr = [1, 2, 3, 4, 5]
        self.H_nom = [8, 8, 8, 8, 8]
        self.zitr = [self.z[6], self.z[7], self.z[8], self.z[9], self.z[10]]

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
        l = self.summ_lpyt()
        self.q_yd = self.Q_max / l

    def get_Q_pyt(self):
        self.Q_pyt = {}
        for i in self.lpyt:
            for k in self.bind:
                if k[0] == i:
                    n1 = k[1]
                    n2 = k[2]
                    ind = str(n1) + str(n2)
            self.Q_pyt[ind] = self.q_yd * self.l[i]

    def get_different_Q(self):
        tempqf = 0
        for k, i in enumerate(self.ring_1[::-1]):
            kn1 = str(i[1])
            kn2 = str(i[2])
            ind = kn1 + kn2
            if k == 0:
                x = self.x_h
                k = x
                sec = '34'
            else:
                x = 0.5
                k = 1
                sec = ind
            self.Q_tr[ind] = tempqf
            self.Q_r[ind] = self.Q_yz.get(kn2, 0) + x * self.Q_pyt.get(sec, 0) + self.Q_tr[ind]
            self.Q_f[ind] = self.Q_yz.get(kn2, 0) + k * self.Q_pyt.get(sec, 0) + self.Q_tr[ind]

            tempqf = self.Q_f[ind]
        tempqf = 0
        for p, s in enumerate(self.ring_2):
            kn1 = str(s[1])
            kn2 = str(s[2])
            ind = kn1 + kn2
            if p == 0:
                y = self.y_h
                k = y
                sec = '34'
            else:
                y = 0.5
                k = 1
                sec = ind
            self.Q_tr[ind] = tempqf
            self.Q_r[ind] = self.Q_yz.get(kn1, 0) + y * self.Q_pyt.get(sec, 0) + self.Q_tr[ind]
            self.Q_f[ind] = self.Q_yz.get(kn1, 0) + k * self.Q_pyt.get(sec, 0) + self.Q_tr[ind]
            tempqf = self.Q_f[ind]
        self.Q_r['61'] = self.Q_f['12'] + self.Q_f['51']
        self.Q_r['34'] = self.Q_r['30'] + self.Q_r['04']

    def get_d(self):
        self.d = {}
        for i in self.ring_1:
            kn1 = i[1]
            kn2 = i[2]
            ind = str(kn1) + str(kn2)
            self.d[ind] = math.sqrt((4 * self.Q_r[ind]) / (math.pi * self.SPEED))
            print('Диаметр равен:', self.d[ind])
            self.d[ind] = float(input('Введите Диаметр по таблице:'))
        for s in self.ring_2:
            kn1 = s[1]
            kn2 = s[2]
            ind = str(kn1) + str(kn2)
            self.d[ind] = math.sqrt((4 * self.Q_r[ind]) / (math.pi * self.SPEED))
            print('Диаметр равен:', self.d[ind])
            self.d[ind] = float(input('Введите Диаметр по таблице:'))
        self.d['34'] = self.d['30']
        self.d['61'] = math.sqrt((4 * self.Q_r['61']) / (math.pi * self.SPEED))
        print('Диаметр равен:', self.d['61'])
        self.d['61'] = float(input('Введите Диаметр по таблице:'))

    def link_a_ring(self):
        self.kt = self.ke + self.sigma * 25
        self.h = {}
        summ = 0
        lng = len(self.ring_1)
        nm1 = self.ring_1[lng - 1][1]
        nm2 = self.ring_2[0][2]
        cen = str(nm1) + str(nm2)
        for i in self.ring:
            kn1 = i[1]
            kn2 = i[2]
            ind = str(kn1) + str(kn2)
            li = i[0]
            self.h[ind] = self.calc_h(self.l[li], self.Q_r[ind], self.d[ind])
            summ = summ + (self.h[ind] * i[3])
        self.y_h = summ / (-2 * self.h[cen])
        self.x_h = 1 - self.y_h
        self.h['61'] = self.calc_h(self.l[3], self.Q_r['61'], self.d['61'])
        print(self.y_h, self.x_h)

    def dict_point(self):
        const_h = self.h['61']
        ms = 0
        for i in range(1, 4):
            hind1 = self.knot_1[i]
            hind2 = self.knot_1[i - 1]
            hind = str(hind2) + str(hind1)
            if i == 1:
                ind = str(self.knot_1[i])
                self.slossh[ind] = const_h
                ms = self.slossh[ind]
            else:
                ind = str(self.knot_1[i])
                self.slossh[ind] = ms + self.h[hind]
                ms = self.slossh[ind]
        ms = 0
        for i in range(1, 4):
            hind1 = self.knot_2[i]
            hind2 = self.knot_2[i - 1]
            hind = str(hind1) + str(hind2)
            if i == 1:
                ind = str(self.knot_2[i])
                self.slossh[ind] = const_h
                ms = self.slossh[ind]
            else:
                ind = str(self.knot_2[i])
                self.slossh[ind] = ms + self.h[hind]
                ms = self.slossh[ind]
        d = {}
        for i in range(0, 5):
            temp = str(self.itr[i])
            d[temp] = self.zitr[i] + self.slossh[temp] + self.H_nom[i]
        for k, i in enumerate(d.items()):
            if k == 0:
                max = i[1]
                point = i[0]
            elif i[1] > max:
                max = i[1]
                point = i[0]
        print(max, point)
        self.pointd = (point, max)

    def calc_watertower(self):
        self.Q_daily_max = self.Q_r['61'] * 24 * 3600 #self.q_daily_max + self.q_mft * 3600 * 24 + self.q_shed * 3600 * 24
        self.V_r = 0.052 * self.Q_daily_max
        self.V_pz = self.q_poz * self.t_poz
        self.V_b = self.V_r + self.V_pz
        self.H_b = self.pointd[1] - self.z[3]
        print(self.H_b)
        print('v_b:', self.V_b)

    def get_fact_h_point(self):
        self.fact_h_p = {}
        self.fact_h_p['1'] = self.z[3] - self.z[6] + self.H_b - self.h['61']
        self.fact_h_p['2'] = self.z[6] - self.z[7] + self.fact_h_p['1'] - self.h['12']
        self.fact_h_p['3'] = self.z[7] - self.z[8] + self.fact_h_p['2'] - self.h['23']
        self.fact_h_p['5'] = self.z[6] - self.z[10] + self.fact_h_p['1'] - self.h['51']
        self.fact_h_p['4'] = self.z[10] - self.z[9] + self.fact_h_p['5'] - self.h['45']

    def get_otv(self):
        self.h_zap4 = self.fact_h_p['2'] - self.h_potr[2]
        self.h_zap5 = self.fact_h_p['5'] - self.h_potr[3]
        self.d_otv4 = ((0.009 * (self.kt ** 0.25) * self.l[8] * (self.q_mft ** 2)) / self.h_zap4) ** (1 / 5.25)
        self.d_otv5 = ((0.009 * (self.kt ** 0.25) * self.l[6] * (self.q_shed ** 2)) / self.h_zap5) ** (1 / 5.25)
        print('Диаметр равен:', self.d_otv4)
        self.d_otv4 = float(input('Введите Диаметр по таблице:'))
        print('Диаметр равен:', self.d_otv5)
        self.d_otv5 = float(input('Введите Диаметр по таблице:'))

    def get_Q_trn(self):
        self.Q_trn = (0.055 * self.Q_daily_max) / 3600

    def getvsnagparam(self):
        self.d['nag'] = math.sqrt((4 * self.Q_trn) / (math.pi * self.SPEED))
        print('Диаметр равен:', self.d['nag'])
        self.d['nag'] = float(input('Введите Диаметр по таблице:'))
        self.d['vs'] = self.d['nag']
        self.lvs = 0
        self.lnag = abs(self.z[1]) + self.l[2] + abs(self.z[3]) + self.H_b
        self.kinetic_V = 1.006e-6

    def get_lmbda(self):
        self.Revs = (self.SPEED * self.d['vs']) / self.kinetic_V
        self.Renag = (self.SPEED * self.d['nag']) / self.kinetic_V
        self.lmbdanag = self.calclmbda(self.Renag, self.d['nag'])
        self.lmbdavs = self.calclmbda(self.Renag, self.d['nag']) #Тут исправить наверн

    def Network_char(self):
        self.A_kf = self.getA()

    def calc_h(self, l, q, d):
        res = (1.05 * 0.009 * (self.kt ** 0.25) * l * (q ** 2)) / (d ** 5.25)
        return res

    def getA(self, lmdvs, lmdnag, lvs, lnag, dvs, dnag, msvs, msnag):
        res = (8 / ((math.pi ** 2) * self.g)) * (lmdvs * (lvs / (dvs ** 5)) + (msvs / (dvs ** 4))
                                                 + lmdnag * (lnag / (dnag ** 5)) + (msnag / (dnag ** 4)))
        return res

    def calclmbda(self, re, d, dl=0.005):
        s1 = (10 * d) / dl
        s2 = (500 * d) / dl
        if re < self.Re_kr:
            lmd = 63 / re
        elif re <= s1:
            lmd = 0.316 / (re ** (1 / 4))
        elif re <= s2:
            lmd = 0.11 * ((dl / d) + 68 / re) ** 0.25
        elif re > s2:
            lmd = 0.11 * (dl / d) ** 0.25
        return lmd

    def my_summ(self, *args):
        k = 0
        for i in args:
            k += i
        return k

    def summ_lpyt(self):
        r = 0
        for i in self.lpyt:
            r += self.l[i]
        return r

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
        self.get_different_Q()
        self.get_d()
        self.dict_point()
        self.calc_watertower()
        self.get_fact_h_point()
        self.get_otv()
        #print(self.slossh)
        #print('Готово', self.y_h, self.x_h)
